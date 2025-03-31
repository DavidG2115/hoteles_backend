from rest_framework import generics, serializers, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Reservacion, SolicitudModificacionReservacion
from .serializers import ReservacionSerializer, SolicitudModificacionSerializer
from hoteles.models import Habitacion
from django.shortcuts import get_object_or_404
from hoteles.models import Habitacion
from hoteles.serializers import HabitacionSerializer
from rest_framework.response import Response
from django.core.mail import send_mail
from .permissions import EsAdministradorOGerente  # 🔹 Importar el nuevo permiso
from usuarios.permissions import PerteneceAlHotel
from usuarios.models import EmpleadoHotel
from .decorators import verificar_reservacion_activa, verificar_usuario_pertenece_al_hotel, verificar_recepcionista_pertenece_hotel


# 🔹 Crear una Reservación
class CrearReservacionView(generics.CreateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        habitacion = get_object_or_404(Habitacion, id=self.request.data['habitacion'])

        if not habitacion.disponible:
            raise serializers.ValidationError("Esta habitación no está disponible.")

        # Guarda la reservación (el email será enviado automáticamente desde signals.py)
        usuario = self.request.user if self.request.user.is_authenticated else None
        serializer.save(usuario=usuario)


# Eliminar una reservación (Solo administradores y gerentes)
class EliminarReservacionView(generics.DestroyAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    lookup_field = "folio"
    permission_classes = [IsAuthenticated, EsAdministradorOGerente, PerteneceAlHotel]

    @verificar_usuario_pertenece_al_hotel
    def delete(self, request, *args, **kwargs):
        reservacion = self.get_object()

        if reservacion.estado == "confirmada":
            raise PermissionDenied("No puedes eliminar una reservación que ya fue confirmada.")

        reservacion_data = ReservacionSerializer(reservacion).data
        response = super().delete(request, *args, **kwargs)
        return Response(
            {"mensaje": "Reservación eliminada exitosamente.", "reservacion": reservacion_data},
            status=status.HTTP_200_OK
        )
    
    
# 🔹 Consultar una reservación por folio (Público)
class ReservacionDetailView(generics.RetrieveAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [AllowAny]  # 🔹 Cualquier usuario puede consultar una reservación

    def get_object(self):
        folio = self.kwargs["folio"]
        return get_object_or_404(Reservacion, folio=folio)
    
# 🔹 Cancelar una reservación (Solo administradores y gerentes)class CancelarReservacionView(generics.UpdateAPIView):
class CancelarReservacionView(generics.UpdateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente, PerteneceAlHotel]

    @verificar_reservacion_activa
    @verificar_usuario_pertenece_al_hotel
    def patch(self, request, *args, **kwargs):
        reservacion = self.get_object()
        reservacion.estado = "cancelada"
        reservacion.save()

        send_mail(
            "Cancelación de Reservación",
            f"Estimado {reservacion.nombre_cliente},\n\n"
            f"Su reservación con folio {reservacion.folio} ha sido cancelada.",
            "noreply@hoteles.com",
            [reservacion.email_cliente],
            fail_silently=True
        )

        return Response({"mensaje": "Reservación cancelada y notificada al cliente."}, status=status.HTTP_200_OK)

    
# 🔹 Modificar una reservación (Solo administradores y gerentes)
class ModificarReservacionView(generics.UpdateAPIView):
    queryset = Reservacion.objects.all()
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente, PerteneceAlHotel]

    @verificar_reservacion_activa
    @verificar_usuario_pertenece_al_hotel
    def patch(self, request, *args, **kwargs):
        reservacion = get_object_or_404(Reservacion, folio=self.kwargs["folio"])

        # Modificar solo ciertos campos
        reservacion.fecha_inicio = request.data.get("fecha_inicio", reservacion.fecha_inicio)
        reservacion.fecha_fin = request.data.get("fecha_fin", reservacion.fecha_fin)
        reservacion.estado = request.data.get("estado", reservacion.estado)
        reservacion.save()

        return Response({"mensaje": "Reservación actualizada y notificada al cliente."}, status=status.HTTP_200_OK)
    
    
# 🔹 Listar reservaciones de su hotel (Solo administradores y gerentes)
class ReservacionesHotelView(generics.ListAPIView):
    serializer_class = ReservacionSerializer
    permission_classes = [EsAdministradorOGerente]  # 🔹 Solo autenticados

    def get_queryset(self):
        hotel_id = self.kwargs["hotel_id"]
        user = self.request.user

        # Verifica explícitamente que el usuario pertenece al hotel consultado
        pertenece = EmpleadoHotel.objects.filter(usuario=user, hotel_id=hotel_id).exists()

        if not pertenece:
            raise PermissionDenied("No perteneces a este hotel.")

        return Reservacion.objects.filter(habitacion__hotel_id=hotel_id)
    
    
class CrearSolicitudModificacionView(generics.CreateAPIView):
    queryset = SolicitudModificacionReservacion.objects.all()
    serializer_class = SolicitudModificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @verificar_recepcionista_pertenece_hotel
    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)
        
        
class AprobarSolicitudView(generics.UpdateAPIView):
    queryset = SolicitudModificacionReservacion.objects.all()
    serializer_class = SolicitudModificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @verificar_usuario_pertenece_al_hotel
    def patch(self, request, *args, **kwargs):
        solicitud = self.get_object()

        if solicitud.estado in ["aprobada", "rechazada"]:
            raise PermissionDenied("Esta solicitud ya ha sido procesada.")

        serializer = self.get_serializer(solicitud, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()

        reservacion = solicitud.reservacion

        # Procesar si fue aprobada
        if solicitud.estado == "aprobada":
            reservacion._desde_solicitud_aprobada = True

            if solicitud.tipo == "eliminacion":
                reservacion.estado = "cancelada"
                reservacion.habitacion.disponible = True
                reservacion.habitacion.save()
            elif solicitud.tipo == "modificacion":
                reservacion.estado = "modificada"

            reservacion.save()

        return Response({"mensaje": "Solicitud procesada correctamente."}, status=status.HTTP_200_OK)

    
    # listar solicitudes pendientes de reservaciones (Solo administradores y gerentes)
class SolicitudesPendientesView(generics.ListAPIView):
    serializer_class = SolicitudModificacionSerializer
    permission_classes = [permissions.IsAuthenticated, EsAdministradorOGerente]

    def get_queryset(self):
        user = self.request.user

        # Obtener hoteles donde trabaja el gerente
        hoteles_ids = EmpleadoHotel.objects.filter(usuario=user).values_list("hotel_id", flat=True)

        # Filtrar solicitudes pendientes de reservaciones que pertenecen a esos hoteles
        return SolicitudModificacionReservacion.objects.filter(
            estado="pendiente",
            reservacion__habitacion__hotel_id__in=hoteles_ids
        )