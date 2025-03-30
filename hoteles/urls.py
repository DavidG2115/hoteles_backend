from django.urls import path
from .views import HotelListCreateView, HotelDetailView, HabitacionListCreateView, HabitacionDetailView, ActualizarLimpiezaHabitacionView, ActualizarMantenimientoHabitacionView

urlpatterns = [
    path('hoteles/', HotelListCreateView.as_view(), name='hoteles_lista'),
    path('hoteles/<int:pk>/', HotelDetailView.as_view(), name='hotel_detalle'),
    path('hoteles/<int:hotel_id>/habitaciones/', HabitacionListCreateView.as_view(), name='habitaciones_lista'),
    path('habitaciones/<int:pk>/', HabitacionDetailView.as_view(), name='habitacion_detalle'),
    path('habitaciones/<int:pk>/estado-limpieza/', ActualizarLimpiezaHabitacionView.as_view()),
    path('habitaciones/<int:pk>/estado-mantenimiento/', ActualizarMantenimientoHabitacionView.as_view()),
]
