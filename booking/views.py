from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages # Pour les messages de succès/erreur
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic


# Create your views here.
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Service,Appointment
from .utils import get_available_slots # On importe notre cerveau

def booking_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    
    # Par défaut, on regarde pour demain (ou la date passée en GET ?date=YYYY-MM-DD)
    date_str = request.GET.get('date')
    if date_str:
        search_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
    else:
        search_date = timezone.now().date() + timezone.timedelta(days=1)

    # Appel de la logique métier
    slots = get_available_slots(service, search_date)

    context = {
        'service': service,
        'search_date': search_date,
        'slots': slots,
    }
    return render(request, 'booking/booking_list.html', context)


@login_required # Oblige l'utilisateur à être connecté
def confirm_booking(request, service_id, date_str, time_str):
    service = get_object_or_404(Service, id=service_id)
    
    # Reconstitution de l'objet datetime complet
    full_date_str = f"{date_str} {time_str}"
    booking_date = timezone.datetime.strptime(full_date_str, "%Y-%m-%d %H:%M")
    
    # On rend la date "aware" (avec fuseau horaire)
    booking_date = timezone.make_aware(booking_date)

    # 1. Vérification ultime de sécurité (Double Check)
    # On réutilise notre logique models.py pour voir si ça bloque
    appointment = Appointment(
        user=request.user,
        service=service,
        date=booking_date
    )

    try:
        appointment.full_clean() # Cela appelle la méthode .clean() du modèle !
        appointment.save()
        messages.success(request, "Votre rendez-vous a été confirmé avec succès !")
    # ... (dans le bloc try/except) ...
    except ValidationError as e:
        messages.error(request, f"Erreur : {e}")
    
    # AVANT : return redirect('booking_view', service_id=service.id)
    # APRÈS :
    return redirect('my_appointments')
# ... imports existants ...

@login_required
def my_appointments(request):
    # On récupère les RDV de l'utilisateur, triés du plus récent au plus ancien
    appointments = Appointment.objects.filter(user=request.user).order_by('date')
    return render(request, 'booking/my_appointments.html', {'appointments': appointments})

@login_required
def cancel_appointment(request, appointment_id):
    # On utilise get_object_or_404 pour être sûr que le RDV existe
    # ET on ajoute user=request.user pour être sûr qu'on ne supprime pas le RDV d'un autre !
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Rendez-vous annulé avec succès.")
        return redirect('my_appointments')
    
    # Si on arrive ici sans POST (par erreur), on redirige juste
    return redirect('my_appointments')



class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login') # Redirige vers login après inscription
    template_name = 'registration/signup.html'

# Ajoute cet import si tu ne l'as pas
from .models import Service 

def home_view(request):
    services = Service.objects.all() # On récupère tous les services (coupes)
    return render(request, 'home.html', {'services': services})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import Appointment

# 1. LE TABLEAU DE BORD (Visible seulement par le staff)
@staff_member_required
def manager_dashboard(request):
    # On récupère tous les RDV, du plus récent au plus ancien
    appointments = Appointment.objects.all().order_by('-date')
    return render(request, 'manager/dashboard.html', {'appointments': appointments})

# 2. L'ACTION DE CHANGER LE STATUT
@staff_member_required
def change_status(request, appointment_id, new_status):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = new_status
    appointment.save()
    return redirect('manager_dashboard') # On recharge la page