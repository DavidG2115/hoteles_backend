from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Hotel, Habitacion
from rest_framework.response import Response
from .serializers import HotelSerializer, HabitacionSerializer, HabitacionPublicSerializer
from .permissions import EsAdministrador
from rest_framework.exceptions import PermissionDenied
from usuarios.permissions import EsJefeCamaristas, EsJefeMantenimiento
from .models import Habitacion
from usuarios.models import EmpleadoHotel

# 🔹 Listar Habitaciones Disponibles (Todos pueden ver ) 
class DisponibilidadHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        if hotel_id and fecha_inicio and fecha_fin:
            return Habitacion.objects.filter(
                hotel_id=hotel_id,
                disponible=True
            )
        return Habitacion.objects.none()
# 🔹 Listar Hoteles (Todos pueden ver, solo administradores pueden crear, editar y eliminar)
class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [EsAdministrador()]  # 🔹 Solo administradores pueden modificar hoteles
        return [AllowAny()]  # 🔹 Cualquier usuario puede ver hoteles

    def perform_create(self, serializer):
        serializer.save()

# 🔹 Ver, Editar y Eliminar un Hotel (Solo administradores)
class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [EsAdministrador]  # 🔹 Solo administradores pueden modificar hoteles

# 🔹 Listar Habitaciones de un Hotel (Todos pueden ver, solo administradores pueden agregar)
class HabitacionListCreateView(generics.ListCreateAPIView):
    serializer_class = HabitacionSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [EsAdministrador()]  # 🔹 Solo administradores pueden agregar habitaciones
        return [AllowAny()]  # 🔹 Cualquier usuario puede ver habitaciones

    def get_queryset(self):
        hotel_id = self.kwargs['hotel_id']
        return Habitacion.objects.filter(hotel_id=hotel_id)

    def perform_create(self, serializer):
        hotel_id = self.kwargs["hotel_id"]

        # Validar que el hotel exista y pertenezca al usuario autenticado
        try:
            hotel = Hotel.objects.get(id=hotel_id, propietario=self.request.user)
        except Hotel.DoesNotExist:
            raise PermissionDenied("No puedes crear habitaciones para este hotel.")

        serializer.save(hotel=hotel)

# 🔹 Ver, Editar y Eliminar una Habitación (Solo administradores)
class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [EsAdministrador]  # 🔹 Solo administradores pueden modificar habitaciones

# 🔹 View para actualizar estado de limpieza
class ActualizarEstadoLimpiezaView(APIView):
    permission_classes = [IsAuthenticated, EsJefeCamaristas]

    def patch(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
            return Response({"error": "Habitación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get("estado_limpieza")
        if nuevo_estado not in dict(Habitacion.ESTADOS_LIMPIEZA):
            return Response({"error": "Estado de limpieza no válido."}, status=status.HTTP_400_BAD_REQUEST)

        habitacion.estado_limpieza = nuevo_estado
        habitacion.save()
        return Response({"mensaje": "Estado de limpieza actualizado correctamente."})

# 🔹 View para actualizar estado de mantenimiento
class ActualizarEstadoMantenimientoView(APIView):
    permission_classes = [IsAuthenticated, EsJefeMantenimiento]

    def patch(self, request, pk):
        try:
            habitacion = Habitacion.objects.get(pk=pk)
        except Habitacion.DoesNotExist:
            return Response({"error": "Habitación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        nuevo_estado = request.data.get("estado_mantenimiento")
        if nuevo_estado not in dict(Habitacion.ESTADOS_MANTENIMIENTO):
            return Response({"error": "Estado de mantenimiento no válido."}, status=status.HTTP_400_BAD_REQUEST)

        habitacion.estado_mantenimiento = nuevo_estado
        habitacion.save()
        return Response({"mensaje": "Estado de mantenimiento actualizado correctamente."})
    
    
class MisHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user

        # Buscar a qué hotel está asignado el usuario
        hoteles = EmpleadoHotel.objects.filter(usuario=usuario).values_list("hotel_id", flat=True)

        # Si es propietario (administrador), incluir también sus hoteles
        if usuario.rol == "administrador":
            hoteles_propios = usuario.hoteles.values_list("id", flat=True)
            hoteles = list(hoteles) + list(hoteles_propios)

        return Habitacion.objects.filter(hotel_id__in=hoteles)