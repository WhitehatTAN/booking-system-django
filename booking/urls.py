from django.urls import path
from . import views

urlpatterns = [
    # ... tes urls existantes ...
    path('<int:service_id>/', views.booking_view, name='booking_view'),
    path('confirm/<int:service_id>/<str:date_str>/<str:time_str>/', views.confirm_booking, name='confirm_booking'),
    
    # NOUVELLES URLs
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/update/<int:appointment_id>/<str:new_status>/', views.change_status, name='change_status'),
]