from django.contrib import admin
from .models import Hotel, Habitacion

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'phone', 'owner']
    list_filter = ['owner']

@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ['number', 'type', 'price_per_night', 'available', 'cleaning_status', 'maintenance_status']
    list_filter = ['type', 'available', 'cleaning_status', 'maintenance_status']
