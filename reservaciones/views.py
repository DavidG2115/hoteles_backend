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

        # 🔹 NO marcamos como no disponible todavía
        # habitacion.disponible = False
        # habitacion.save()

        reservacion = serializer.save()

        # 🔹 Enviar correo automático al cliente
        from django.core.mail import send_mail

        send_mail(
            "Reserva Recibida - Hoteles de Morelia",
            f"Hola {reservacion.nombre_cliente},\n\n"
            f"Gracias por reservar con nosotros. Tu reservación con folio {reservacion.folio} está registrada como *pendiente*.\n\n"
            f"Por favor realiza el pago correspondiente y envía tu comprobante al correo del hotel para confirmar tu reservación.\n\n"
            f"Hotel: {habitacion.hotel.nombre}\n"
            f"Dirección: {habitacion.hotel.direccion}\n"
            f"Teléfono: {habitacion.hotel.telefono}\n\n"
            f"Fecha de entrada: {reservacion.fecha_inicio}\n"
            f"Fecha de salida: {reservacion.fecha_fin}\n"
            f"Habitación: {habitacion.numero} ({habitacion.tipo})\n"
            f"Costo por noche: ${habitacion.costo_por_noche}\n"
            f"Folio: {reservacion.folio}\n\n"
            f"➡️ IMPORTANTE: Envía el comprobante a: contacto@hotelmorelia.com\n\n"
            f"Gracias por tu preferencia.",
            "noreply@hoteles.com",
            [reservacion.email_cliente],
            fail_silently=True
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
        solicitud = self.get_serializer(solicitud, data=request.data, partial=True)
        solicitud.is_valid(raise_exception=True)
        solicitud = solicitud.save()

        reservacion = solicitud.reservacion

        if solicitud.estado == "aprobada":
            if solicitud.tipo == "eliminacion":
                reservacion.estado = "cancelada"
                reservacion.habitacion.disponible = True
                reservacion.habitacion.save()
            elif solicitud.tipo == "modificacion":
                reservacion.estado = "modificada"
            reservacion.save()

            send_mail(
                "Actualización de Reservación",
                f"Estimado {reservacion.nombre_cliente},\n\n"
                f"Su reservación con folio {reservacion.folio} ha sido actualizada.",
                "noreply@hoteles.com",
                [reservacion.email_cliente],
                fail_silently=True
            )

        return Response({"mensaje": "Solicitud procesada correctamente."}, status=status.HTTP_200_OK)
    
    # listar solicitudes pendientes de reservaciones (Solo administradores y gerentes)
class SolicitudesPendientesView(generics.ListAPIView):
    serializer_class = SolicitudModificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Validar que sea gerente
        if user.rol != "administrador" and user.rol != "gerente":
            return SolicitudModificacionReservacion.objects.none()

        # Obtener hoteles donde trabaja el gerente
        hoteles_ids = EmpleadoHotel.objects.filter(usuario=user).values_list("hotel_id", flat=True)

        # Filtrar solicitudes pendientes de reservaciones que pertenecen a esos hoteles
        return SolicitudModificacionReservacion.objects.filter(
            estado="pendiente",
            reservacion__habitacion__hotel_id__in=hoteles_ids
        )