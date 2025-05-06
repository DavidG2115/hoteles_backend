from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Hotel, Habitacion
from usuarios.models import EmpleadoHotel
from reservaciones.models import Reservacion
from .permissions import EsAdministrador
from usuarios.permissions import EsJefeCamaristas, EsJefeMantenimiento
from .serializers import (
    HotelSerializer,
    HabitacionSerializer,
    HabitacionPublicSerializer,
    HotelWithRoomsSerializer,
)

# ✅ Listar habitaciones disponibles por fecha y hotel
class DisponibilidadHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        habitaciones_ocupadas = Reservacion.objects.filter(
            habitacion__hotel_id=hotel_id,
            estado__in=["pendiente", "confirmada", "modificada"],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        ).values_list("habitacion_id", flat=True)

        return Habitacion.objects.filter(
            hotel_id=hotel_id,
            available=True
        ).exclude(id__in=habitaciones_ocupadas)

# ✅ Listar y crear hoteles
class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [EsAdministrador()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save()

# ✅ Ver, editar, eliminar hotel
class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [EsAdministrador]

# ✅ NUEVA: Ver hotel con habitaciones anidadas
class HotelWithRoomsView(generics.RetrieveAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelWithRoomsSerializer
    permission_classes = [AllowAny]

# ✅ Listar y crear habitaciones de un hotel
class HabitacionListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [EsAdministrador()]
        return [AllowAny()]

    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Habitacion.objects.filter(hotel_id=hotel_id)

    def perform_create(self, serializer):
        hotel_id = self.kwargs["hotel_id"]
        try:
            hotel = Hotel.objects.get(id=hotel_id, owner=self.request.user)
        except Hotel.DoesNotExist:
            raise PermissionDenied("No puedes crear habitaciones para este hotel.")
        serializer.save(hotel=hotel)

# ✅ Ver, editar, eliminar habitación
class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [EsAdministrador()]
        return [AllowAny()]

# ✅ Actualizar estado de limpieza
class ActualizarEstadoLimpiezaView(APIView):
    permission_classes = [IsAuthenticated, EsJefeCamaristas]

    def patch(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get("cleaning_status")
        if nuevo_estado not in dict(Habitacion.CLEANING_STATUS):
            return Response({"error": "Invalid cleaning status."}, status=status.HTTP_400_BAD_REQUEST)

        habitacion.cleaning_status = nuevo_estado
        habitacion.save()
        return Response({"message": "Cleaning status updated successfully."})

# ✅ Actualizar estado de mantenimiento
class ActualizarEstadoMantenimientoView(APIView):
    permission_classes = [IsAuthenticated, EsJefeMantenimiento]

    def patch(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
            return Response({"error": "Room not found."}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get("maintenance_status")
        if nuevo_estado not in dict(Habitacion.MAINTENANCE_STATUS):
            return Response({"error": "Invalid maintenance status."}, status=status.HTTP_400_BAD_REQUEST)

        habitacion.maintenance_status = nuevo_estado
        habitacion.save()
        return Response({"message": "Maintenance status updated successfully."})

# ✅ Listar habitaciones donde trabaja o administra el usuario
class MisHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        hoteles_empleado = EmpleadoHotel.objects.filter(
            usuario=usuario
        ).values_list("hotel_id", flat=True)

        hoteles_propios = usuario.hotels.values_list("id", flat=True) if usuario.rol == "administrador" else []

        hoteles_ids = set(hoteles_empleado).union(hoteles_propios)

        return Habitacion.objects.filter(hotel_id__in=hoteles_ids)
