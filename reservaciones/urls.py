from django.urls import path
from .views import *

urlpatterns = [
    path('reservaciones/crear/', CrearReservacionView.as_view(), name='crear_reservacion'),
    path('reservaciones/<uuid:folio>/', ReservacionDetailView.as_view(), name='detalle_reservacion'),
    path('reservaciones/<uuid:folio>/cancelar/', CancelarReservacionView.as_view(), name='cancelar_reservacion'),
    path('reservaciones/<uuid:folio>/editar/', ModificarReservacionView.as_view(), name='editar_reservacion'),
    path('hoteles/<int:hotel_id>/reservaciones/', ReservacionesHotelView.as_view(), name='reservaciones_hotel'),
    path('crear/solicitud/', CrearSolicitudModificacionView.as_view(), name='crear_solicitud'),
    path('solicitudes/<int:pk>/', AprobarSolicitudView.as_view(), name='aprobar_solicitud'),
    path("solicitudes/pendientes/", SolicitudesPendientesView.as_view(), name="solicitudes-pendientes"),
]
