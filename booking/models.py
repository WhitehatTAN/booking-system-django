from django.db import models

# Create your models here.
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

# 1. Le Service proposé
class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom du service")
    description = models.TextField(blank=True, verbose_name="Description")
    duration = models.DurationField(verbose_name="Durée du service")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Prix")
    
    # --- NOUVEAU CHAMP ---
    # upload_to='services/' va créer un dossier 'services' dans 'media'
    image = models.ImageField(upload_to='services/', blank=True, null=True, verbose_name="Photo du service")

    def __str__(self):
        return f"{self.name} ({self.duration})"
# 2. Les Disponibilités (Créneaux ouverts)
class Availability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="availabilities")
    start_time = models.DateTimeField(verbose_name="Début du créneau")
    end_time = models.DateTimeField(verbose_name="Fin du créneau")

    def __str__(self):
        return f"{self.service.name} : {self.start_time.strftime('%d/%m %H:%M')} - {self.end_time.strftime('%H:%M')}"

    def clean(self):
        # Vérif basique : la fin doit être après le début
        if self.end_time <= self.start_time:
            raise ValidationError("La fin du créneau doit être après le début.")

# 3. Le Rendez-vous (La réservation réelle)
class Appointment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="appointments")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    date = models.DateTimeField(verbose_name="Date et Heure du RDV")
    created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('CONFIRMED', 'Confirmé'),
        ('DONE', 'Terminé'),
        ('CANCELLED', 'Annulé'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.service.name} le {self.date.strftime('%d/%m à %H:%M')}"

    def get_end_time(self):
        """Calcule l'heure de fin basée sur la durée du service"""
        return self.date + self.service.duration

    def clean(self):
        """
        C'est ICI que l'on empêche les conflits (doublons).
        On vérifie s'il existe déjà un RDV qui chevauche celui qu'on essaie de créer.
        """
        if not self.service or not self.date:
            return

        appt_start = self.date
        appt_end = self.get_end_time()

        # On cherche des conflits pour le MÊME service (ou globalement selon ton besoin)
        # Ici, on suppose qu'un service ne peut être fait qu'une fois à la fois.
        overlapping_appts = Appointment.objects.filter(
            service=self.service,
            date__lt=appt_end, # Commence avant que je finisse
        ).exclude(pk=self.pk) # S'exclure soi-même en cas d'édition

        # Vérification précise des chevauchements
        for appt in overlapping_appts:
            existing_end = appt.get_end_time()
            if existing_end > appt_start:
                raise ValidationError(f"Ce créneau est déjà pris par un autre rendez-vous (Conflit avec {appt}).")

    def save(self, *args, **kwargs):
        self.clean() # Force la validation même via l'admin ou shell
        super().save(*args, **kwargs)
