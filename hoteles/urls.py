from django.urls import path
from .views import HotelListCreateView, HotelDetailView, HabitacionListCreateView, HabitacionDetailView

urlpatterns = [
    path('hoteles/', HotelListCreateView.as_view(), name='hoteles_lista'),
    path('hoteles/<int:pk>/', HotelDetailView.as_view(), name='hotel_detalle'),
    path('hoteles/<int:hotel_id>/habitaciones/', HabitacionListCreateView.as_view(), name='habitaciones_lista'),
    path('habitaciones/<int:pk>/', HabitacionDetailView.as_view(), name='habitacion_detalle'),
]
