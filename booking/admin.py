from django.contrib import admin

# Register your models here.
from .models import Service, Availability, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'price')

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('service', 'start_time', 'end_time')
    list_filter = ('service', 'start_time')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'date', 'created_at')
    list_filter = ('service', 'date')
    search_fields = ('user__username', 'service__name')
