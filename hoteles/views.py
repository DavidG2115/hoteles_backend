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
from reservaciones.models import Reservacion

# Listar Habitaciones Disponibles (Todos pueden ver ) 
class DisponibilidadHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        hotel_id = self.request.query_params.get('hotel')
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')

        # Buscar habitaciones ocupadas en esas fechas
        habitaciones_ocupadas = Reservacion.objects.filter(
            habitacion__hotel_id=hotel_id,
            estado__in=["pendiente", "confirmada", "modificada"],
            fecha_inicio__lt=fecha_fin,
            fecha_fin__gt=fecha_inicio
        ).values_list("habitacion_id", flat=True)

        return Habitacion.objects.filter(
            hotel_id=hotel_id,
            disponible=True,
        ).exclude(id__in=habitaciones_ocupadas)
        
        
# Listar Hoteles (Todos pueden ver, solo administradores pueden crear, editar y eliminar)
class HotelListCreateView(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            return [EsAdministrador()]  
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save()

# Ver, Editar y Eliminar un Hotel (Solo administradores)
class HotelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [EsAdministrador] 

# Listar Habitaciones de un Hotel (Todos pueden ver, solo administradores pueden agregar)
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

# Ver, Editar y Eliminar una Habitación (Solo administradores)
class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [EsAdministrador]  

# View para actualizar estado de limpieza
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

# View para actualizar estado de mantenimiento
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
    
    
# Listar habitaciones de un hotel para ver estados de limpieza y mantenimiento
class MisHabitacionesView(generics.ListAPIView):
    serializer_class = HabitacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario = self.request.user
        hoteles_empleado = EmpleadoHotel.objects.filter(
            usuario=usuario
        ).values_list("hotel_id", flat=True)

        hoteles_propios = usuario.hoteles.values_list("id", flat=True) if usuario.rol == "administrador" else []

        hoteles_ids = set(hoteles_empleado).union(hoteles_propios)

        return Habitacion.objects.filter(hotel_id__in=hoteles_ids)
