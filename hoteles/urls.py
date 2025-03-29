from django.urls import path
from .views import HotelListCreateView, HotelDetailView, HabitacionListCreateView, HabitacionDetailView, ActualizarEstadoLimpiezaView, ActualizarEstadoMantenimientoView, DisponibilidadHabitacionesView, MisHabitacionesView

urlpatterns = [
    path('hoteles/', HotelListCreateView.as_view(), name='hoteles_lista'),
    path('habitaciones/disponibilidad/', DisponibilidadHabitacionesView.as_view()),
    path('hoteles/<int:pk>/', HotelDetailView.as_view(), name='hotel_detalle'),
    path('hoteles/<int:hotel_id>/habitaciones/', HabitacionListCreateView.as_view(), name='habitaciones_lista'),
    path('habitaciones/<int:pk>/', HabitacionDetailView.as_view(), name='habitacion_detalle'),
    path("habitaciones/<int:pk>/estado-limpieza/", ActualizarEstadoLimpiezaView.as_view(), name="actualizar_estado_limpieza"),
    path("habitaciones/<int:pk>/estado-mantenimiento/", ActualizarEstadoMantenimientoView.as_view(), name="actualizar_estado_mantenimiento"),
    path("habitaciones/mis-habitaciones/", MisHabitacionesView.as_view()),
]
