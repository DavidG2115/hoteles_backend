from django.contrib import admin
from .models import Servicio, ReservacionServicio

# Registrar el modelo Servicio
@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'hotel', 'costo')  # Campos que se mostrarán en la lista
    search_fields = ('nombre', 'hotel__nombre')  # Campos para buscar
    list_filter = ('hotel',)  # Filtros laterales

# Registrar el modelo ReservacionServicio
@admin.register(ReservacionServicio)
class ReservacionServicioAdmin(admin.ModelAdmin):
    list_display = ('reservacion', 'servicio', 'cantidad')  # Campos que se mostrarán en la lista
    search_fields = ('reservacion__folio', 'servicio__nombre')  # Campos para buscar
    list_filter = ('reservacion',)  # Filtros laterales