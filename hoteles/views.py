from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Hotel, Habitacion
from .serializers import HotelSerializer, HabitacionSerializer, HabitacionPublicSerializer
from .permissions import EsAdministrador, EsJefeMantenimiento, EsJefeCamaristas

# 🔹 Listar Hoteles (Todos pueden ver, solo administradores pueden crear, editar y eliminar)
class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [EsAdministrador()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save()

# 🔹 Ver, Editar y Eliminar un Hotel (Solo administradores)
class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [EsAdministrador]

# 🔹 Listar Habitaciones de un Hotel
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
            hotel = Hotel.objects.get(id=hotel_id, propietario=self.request.user)
        except Hotel.DoesNotExist:
            raise PermissionDenied("No puedes crear habitaciones para este hotel.")

        serializer.save(hotel=hotel)

# 🔹 Ver, Editar y Eliminar una Habitación
class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [EsAdministrador]

# 🔹 Consultar disponibilidad de habitaciones
class DisponibilidadHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel', None)
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)

        if hotel_id and fecha_inicio and fecha_fin:
            return Habitacion.objects.filter(
                hotel_id=hotel_id,
                disponible=True
            )
        return Habitacion.objects.none()

# 🔹 Actualizar el estado de mantenimiento de una habitación
class ActualizarMantenimientoHabitacionView(generics.UpdateAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated, EsJefeMantenimiento]

    def patch(self, request, *args, **kwargs):
        habitacion = self.get_object()
        nuevo_estado = request.data.get("estado_mantenimiento")

        if nuevo_estado not in dict(Habitacion.ESTADOS_MANTENIMIENTO):
            return Response({"detalle": "Estado inválido"}, status=400)

        habitacion.estado_mantenimiento = nuevo_estado
        habitacion.save()
        return Response({"mensaje": "Estado de mantenimiento actualizado correctamente."})

# 🔹 Actualizar el estado de limpieza de una habitación
class ActualizarLimpiezaHabitacionView(generics.UpdateAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated, EsJefeCamaristas]

    def patch(self, request, *args, **kwargs):
        habitacion = self.get_object()
        nuevo_estado = request.data.get("estado_limpieza")

        if nuevo_estado not in dict(Habitacion.ESTADOS_LIMPIEZA):
            return Response({"detalle": "Estado inválido"}, status=400)

        habitacion.estado_limpieza = nuevo_estado
        habitacion.save()
        return Response({"mensaje": "Estado de limpieza actualizado correctamente."})
