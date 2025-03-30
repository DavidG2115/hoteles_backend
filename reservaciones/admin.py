from django.contrib import admin
from .models import Reservacion, SolicitudModificacionReservacion

# Registrar el modelo Reservacion
@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ('folio', 'nombre_cliente', 'habitacion', 'fecha_inicio', 'fecha_fin', 'estado')  # Campos visibles
    search_fields = ('folio', 'nombre_cliente', 'email_cliente', 'habitacion__numero')  # Campos para buscar
    list_filter = ('estado', 'fecha_inicio', 'fecha_fin')  # Filtros laterales

# Registrar el modelo SolicitudModificacionReservacion
@admin.register(SolicitudModificacionReservacion)
class SolicitudModificacionReservacionAdmin(admin.ModelAdmin):
    list_display = ('reservacion', 'solicitante', 'tipo', 'estado', 'fecha_solicitud')  # Campos visibles
    search_fields = ('reservacion__folio', 'solicitante__username', 'tipo')  # Campos para buscar
    list_filter = ('tipo', 'estado', 'fecha_solicitud')  # Filtros laterales