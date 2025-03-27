from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Hotel, Habitacion
from .serializers import HotelSerializer, HabitacionSerializer
from .permissions import EsAdministrador

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
        hotel_id = self.kwargs['hotel_id']
        serializer.save(hotel_id=hotel_id)

# 🔹 Ver, Editar y Eliminar una Habitación (Solo administradores)
class HabitacionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer
    permission_classes = [EsAdministrador]  # 🔹 Solo administradores pueden modificar habitaciones
