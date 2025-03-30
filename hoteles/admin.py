from django.contrib import admin
from .models import Hotel, Habitacion

# Registrar el modelo Hotel
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'telefono', 'propietario')  # Campos visibles
    search_fields = ('nombre', 'direccion', 'telefono', 'propietario__username')  # Campos para buscar
    list_filter = ('propietario',)  # Filtros laterales

# Registrar el modelo Habitacion
@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = ('numero', 'hotel', 'tipo', 'costo_por_noche', 'disponible', 'estado_limpieza', 'estado_mantenimiento')  # Campos visibles
    search_fields = ('numero', 'hotel__nombre', 'tipo')  # Campos para buscar
    list_filter = ('hotel', 'tipo', 'disponible', 'estado_limpieza', 'estado_mantenimiento')  # Filtros laterales