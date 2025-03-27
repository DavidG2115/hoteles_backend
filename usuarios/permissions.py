from rest_framework.permissions import BasePermission
from hoteles.models import Hotel
from usuarios.models import EmpleadoHotel

class EsAdministrador(BasePermission):
    """
    Permiso para permitir solo a administradores crear hoteles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "administrador"

class PerteneceAlHotel(BasePermission):
    """
    Permite acceso solo si el usuario es administrador del hotel o está asignado como empleado.
    """

    def has_object_permission(self, request, view, obj):
        # Intentar obtener el hotel desde el objeto
        hotel = None

        if hasattr(obj, 'hotel'):
            hotel = obj.hotel
        elif hasattr(obj, 'habitacion'):
            hotel = obj.habitacion.hotel

        if not hotel:
            return False

        # Si es el propietario (admin del hotel)
        if hotel.propietario == request.user:
            return True

        # Si está asignado como empleado del hotel
        return EmpleadoHotel.objects.filter(usuario=request.user, hotel=hotel).exists()