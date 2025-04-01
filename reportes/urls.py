
from django.urls import path
from .views import ReporteReservacionesView, ReporteServiciosView, ReporteIngresosView

urlpatterns = [
    path('reportes/<int:hotel_id>/reservaciones/', ReporteReservacionesView.as_view(), name='reporte_reservaciones'),
    path('reportes/<int:hotel_id>/ingresos/', ReporteIngresosView.as_view(), name='reporte_ingresos'),
    path('reportes/<int:hotel_id>/servicios/', ReporteServiciosView.as_view(), name='reporte_servicios'),
]

