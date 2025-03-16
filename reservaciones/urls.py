from django.urls import path
from .views import *

urlpatterns = [
    path('habitaciones/disponibilidad/', DisponibilidadHabitacionesView.as_view(), name='disponibilidad_habitaciones'),
    path('reservaciones/', CrearReservacionView.as_view(), name='crear_reservacion'),
    path('reservaciones/<uuid:folio>/', ReservacionDetailView.as_view(), name='detalle_reservacion'),
    path('reservaciones/<uuid:folio>/cancelar/', CancelarReservacionView.as_view(), name='cancelar_reservacion'),
    path('reservaciones/<uuid:folio>/editar/', ModificarReservacionView.as_view(), name='editar_reservacion'),
    path('hoteles/<int:hotel_id>/reservaciones/', ReservacionesHotelView.as_view(), name='reservaciones_hotel'),
]
