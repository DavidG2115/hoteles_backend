from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from hoteles.models import Hotel, Habitacion
from reservaciones.models import Reservacion
from servicios.models import ReservacionServicio
from django.db.models import Sum, Count
from .permissions import EsAdministradorOGerente

from datetime import datetime

class ReporteReservacionesView(APIView):
    permission_classes = [IsAuthenticated, EsAdministradorOGerente]

    def get(self, request, hotel_id):
        inicio = request.GET.get('inicio')
        fin = request.GET.get('fin')

        try:
            inicio = datetime.strptime(inicio, "%Y-%m-%d").date()
            fin = datetime.strptime(fin, "%Y-%m-%d").date()
        except:
            return Response({"error": "Formato de fechas inválido. Usa YYYY-MM-DD."}, status=400)

        reservaciones = Reservacion.objects.filter(
            habitacion__hotel_id=hotel_id,
            fecha_inicio__gte=inicio,
            fecha_fin__lte=fin
        )

        por_estado = reservaciones.values('estado').annotate(total=Count('id'))

        habitaciones_ocupadas = reservaciones.values('habitacion').distinct().count()

        return Response({
            "total_reservaciones": reservaciones.count(),
            "habitaciones_ocupadas": habitaciones_ocupadas,
            "estado_reservaciones": list(por_estado)
        })

class ReporteServiciosView(APIView):
    permission_classes = [IsAuthenticated, EsAdministradorOGerente]

    def get(self, request, hotel_id):
        inicio = request.GET.get('inicio')
        fin = request.GET.get('fin')

        servicios = ReservacionServicio.objects.filter(
            reservacion__habitacion__hotel_id=hotel_id,
            reservacion__fecha_inicio__gte=inicio,
            reservacion__fecha_fin__lte=fin
        ).values('servicio__nombre').annotate(
            total_vendidos=Sum('cantidad')
        )

        return Response({
            "servicios": list(servicios)
        })

class ReporteIngresosView(APIView):
    permission_classes = [IsAuthenticated, EsAdministradorOGerente]

    def get(self, request, hotel_id):
        inicio = request.GET.get('inicio')
        fin = request.GET.get('fin')

        reservas = Reservacion.objects.filter(
            habitacion__hotel_id=hotel_id,
            fecha_inicio__gte=inicio,
            fecha_fin__lte=fin
        ).select_related('habitacion')

        servicios = ReservacionServicio.objects.filter(
            reservacion__habitacion__hotel_id=hotel_id,
            reservacion__fecha_inicio__gte=inicio,
            reservacion__fecha_fin__lte=fin
        ).select_related('servicio')

        total_habitaciones = sum(
            (r.habitacion.costo_por_noche * ((r.fecha_fin - r.fecha_inicio).days)) for r in reservas
        )

        total_servicios = sum(s.servicio.costo * s.cantidad for s in servicios)

        return Response({
            "ingreso_por_habitaciones": total_habitaciones,
            "ingreso_por_servicios": total_servicios,
            "ingreso_total": total_habitaciones + total_servicios
        })

