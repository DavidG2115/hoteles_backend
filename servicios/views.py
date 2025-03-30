from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Servicio, ReservacionServicio
from .serializers import ServicioSerializer, ReservacionServicioSerializer
from hoteles.models import Hotel
from reservaciones.models import Reservacion
from django.shortcuts import get_object_or_404
from .permissions import EsAdministradorOGerente
from django.core.exceptions import ValidationError

# 🔹 Listar y Crear Servicios de un Hotel (Admins pueden crear, todos pueden ver)
class ServicioListCreateView(generics.ListCreateAPIView):
    serializer_class = ServicioSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [EsAdministradorOGerente()]  # 🔹 Solo administradores y gerentes pueden crear
        return [AllowAny()]  # 🔹 Cualquier usuario puede ver los servicios

    def get_queryset(self):
        hotel_id = self.kwargs["hotel_id"]
        return Servicio.objects.filter(hotel_id=hotel_id)

    def perform_create(self, serializer):
        hotel_id = self.kwargs["hotel_id"]
        hotel = get_object_or_404(Hotel, id=hotel_id)
        serializer.save(hotel=hotel)

# 🔹 Ver, Editar y Eliminar un Servicio (Solo Administradores)
class ServicioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [EsAdministradorOGerente]  # 🔹 Solo administradores pueden modificar

# 🔹 Agregar Servicios a una Reservación
class AgregarServicioReservacionView(generics.CreateAPIView):
    queryset = ReservacionServicio.objects.all()
    serializer_class = ReservacionServicioSerializer
    permission_classes = [IsAuthenticated]  # 🔹 Usuarios autenticados pueden agregar servicios

    def perform_create(self, serializer):
        folio = self.kwargs["folio"]
        reservacion = get_object_or_404(Reservacion, folio=folio)

        servicio_id = self.request.data.get("servicio")
        servicio = get_object_or_404(Servicio, id=servicio_id)

        # 🔒 Validar que el servicio pertenezca al mismo hotel que la reservación
        hotel_reservacion = reservacion.habitacion.hotel
        hotel_servicio = servicio.hotel

        if hotel_reservacion.id != hotel_servicio.id:
            raise ValidationError("El servicio no pertenece al hotel de la reservación.")

        # Si pasa la validación, guardar
        serializer.save(reservacion=reservacion, servicio=servicio)
        
# 🔹 Listar servicios asociados a una reservación
class ServiciosReservacionView(generics.ListAPIView):
    serializer_class = ReservacionServicioSerializer
    permission_classes = [IsAuthenticated]  # Puedes cambiarlo a AllowAny si quieres que el turista lo vea sin login

    def get_queryset(self):
        folio = self.kwargs["folio"]
        reservacion = get_object_or_404(Reservacion, folio=folio)
        return ReservacionServicio.objects.filter(reservacion=reservacion)

# 🔹 Editar servicios asociados a una reservación
class EditarServicioReservacionView(generics.UpdateAPIView):
    queryset = ReservacionServicio.objects.all()
    serializer_class = ReservacionServicioSerializer
    permission_classes = [IsAuthenticated] 