from django.urls import path
from .views import ServicioListCreateView, ServicioDetailView, AgregarServicioReservacionView, ServiciosReservacionView

urlpatterns = [
    path('hoteles/<int:hotel_id>/servicios/', ServicioListCreateView.as_view(), name='listar_servicios'),
    path('servicios/<int:pk>/', ServicioDetailView.as_view(), name='detalle_servicio'),
    path('reservaciones/<uuid:folio>/servicios/', AgregarServicioReservacionView.as_view(), name='agregar_servicio_reservacion'),
    path('reservaciones/<uuid:folio>/servicios/listar/', ServiciosReservacionView.as_view(), name='listar_servicios_reservacion'),
]
