from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Reservacion
from .serializers import ReservacionSerializer
from hoteles.models import Habitacion
from django.shortcuts import get_object_or_404
from hoteles.models import Habitacion
from hoteles.serializers import HabitacionSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from .permissions import EsAdministradorOGerente  # 🔹 Importar el nuevo permiso

# 🔹 Verificar disponibilidad de habitaciones por fechas
class DisponibilidadHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionSerializer  # 🔹 Cambiar a HabitacionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)

        if hotel_id and fecha_inicio and fecha_fin:
            return Habitacion.objects.filter(
                hotel_id=hotel_id,
                disponible=True  # 🔹 Solo habitaciones disponibles
            )
        return Habitacion.objects.none()

# 🔹 Crear una Reservación
class CrearReservacionView(generics.CreateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        habitacion = get_object_or_404(Habitacion, id=self.request.data['habitacion'])
        if not habitacion.disponible:
            raise serializers.ValidationError("Esta habitación no está disponible.")
        
        habitacion.disponible = False  # Marcar como no disponible
        habitacion.save()
        serializer.save()

# 🔹 Consultar una reservación por folio (Público)
class ReservacionDetailView(generics.RetrieveAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [AllowAny]  # 🔹 Cualquier usuario puede consultar una reservación

    def get_object(self):
        folio = self.kwargs["folio"]
        return get_object_or_404(Reservacion, folio=folio)
    
# 🔹 Cancelar una reservación (Solo administradores y gerentes)
class CancelarReservacionView(generics.UpdateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente]  # 🔹 Permitir solo a admins y gerentes

    def patch(self, request, *args, **kwargs):
        reservacion = get_object_or_404(Reservacion, folio=self.kwargs["folio"])

        # Marcar la reservación como cancelada
        reservacion.estado = "cancelada"
        reservacion.save()

        # 🔹 Enviar notificación por correo al turista
        send_mail(
            "Cancelación de Reservación",
            f"Estimado {reservacion.nombre_cliente},\n\n"
            f"Su reservación con folio {reservacion.folio} ha sido cancelada por el hotel.",
            "garcdavid2101@gmail.com",
            [reservacion.email_cliente],
            fail_silently=True
        )

        return Response({"mensaje": "Reservación cancelada y notificada al cliente."}, status=status.HTTP_200_OK)
    
# 🔹 Modificar una reservación (Solo administradores y gerentes)
class ModificarReservacionView(generics.UpdateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente]  # 🔹 Permitir solo a admins y gerentes

    def patch(self, request, *args, **kwargs):
        reservacion = get_object_or_404(Reservacion, folio=self.kwargs["folio"])

        # Modificar solo ciertos campos
        reservacion.fecha_inicio = request.data.get("fecha_inicio", reservacion.fecha_inicio)
        reservacion.fecha_fin = request.data.get("fecha_fin", reservacion.fecha_fin)
        reservacion.estado = request.data.get("estado", reservacion.estado)
        reservacion.save()

        # 🔹 Enviar notificación por correo al turista
        send_mail(
            "Actualización de Reservación",
            f"Estimado {reservacion.nombre_cliente},\n\n"
            f"Su reservación con folio {reservacion.folio} ha sido actualizada.\n"
            f"Fecha de entrada: {reservacion.fecha_inicio}\n"
            f"Fecha de salida: {reservacion.fecha_fin}\n"
            f"Estado: {reservacion.estado}",
            "garcdavid2101@gmail.com",
            [reservacion.email_cliente],
            fail_silently=True
        )

        return Response({"mensaje": "Reservación actualizada y notificada al cliente."}, status=status.HTTP_200_OK)
# 🔹 Listar reservaciones de un hotel (Solo administradores)
class ReservacionesHotelView(generics.ListAPIView):
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente]  # 🔹 Solo autenticados

    def get_queryset(self):
        hotel_id = self.kwargs["hotel_id"]
        return Reservacion.objects.filter(habitacion__hotel_id=hotel_id)
    
# 🔹 Listar todas las reservaciones (Solo administradores y gerentes)
class ListarTodasReservacionesView(generics.ListAPIView):  # 🔹 ListAPIView permite GET
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [IsAuthenticated]  # Solo autenticados

    def get_queryset(self):
        # Solo administradores y gerentes pueden ver las reservaciones
        if self.request.user.rol in ["administrador", "gerente"]:
            return Reservacion.objects.all()
        return Reservacion.objects.none()  # Si no es admin/gerente, no devuelve nada