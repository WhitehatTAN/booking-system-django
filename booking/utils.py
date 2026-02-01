import datetime
from django.utils import timezone
from .models import Appointment, Availability

def get_available_slots(service, date_obj):
    """
    Calcule les créneaux libres pour un service donné à une date précise.
    Retourne une liste d'objets datetime (heures de début).
    """
    
    # 1. Récupérer les plages de disponibilité pour ce jour-là
    # On filtre les disponibilités qui chevauchent la journée demandée
    day_start = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.min))
    day_end = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.max))

    availabilities = Availability.objects.filter(
        service=service,
        start_time__date=date_obj # Astuce Django pour filtrer par date exacte
    )

    # 2. Récupérer les RDV existants pour ce service ce jour-là
    existing_appointments = Appointment.objects.filter(
        service=service,
        date__date=date_obj
    ).values_list('date', flat=True)
    
    # Convertir en set pour une recherche ultra-rapide
    # On normalise les dates pour éviter les soucis de secondes/microsecondes
    taken_slots = {appt.replace(second=0, microsecond=0) for appt in existing_appointments}

    free_slots = []

    # 3. L'Algorithme de découpage
    for availability in availabilities:
        # On commence au début de la plage de dispo
        current_slot = availability.start_time
        
        # Tant que (début du créneau + durée du service) <= fin de la dispo
        while current_slot + service.duration <= availability.end_time:
            
            # Vérification : Est-ce que ce créneau est déjà pris ?
            # On normalise aussi l'heure actuelle pour comparer
            normalized_slot = current_slot.replace(second=0, microsecond=0)
            
            if normalized_slot not in taken_slots:
                free_slots.append(current_slot)
            
            # On avance au créneau suivant (ex: +30 min)
            current_slot += service.duration

    return free_slots