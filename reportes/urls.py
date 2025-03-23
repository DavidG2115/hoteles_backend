
from django.urls import path
from .views import ReporteReservacionesView, ReporteServiciosView, ReporteIngresosView

urlpatterns = [
    path('reportes/hotel/<int:hotel_id>/reservaciones/', ReporteReservacionesView.as_view(), name='reporte_reservaciones'),
    path('reportes/hotel/<int:hotel_id>/servicios/', ReporteServiciosView.as_view(), name='reporte_servicios'),
    path('reportes/hotel/<int:hotel_id>/ingresos/', ReporteIngresosView.as_view(), name='reporte_ingresos'),
]

