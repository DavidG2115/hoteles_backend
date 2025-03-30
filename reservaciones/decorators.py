from functools import wraps
from rest_framework.exceptions import PermissionDenied
from usuarios.models import EmpleadoHotel

def verificar_reservacion_activa(func):
    """
    Verifica que una reservación esté activa (no cancelada).
    """
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        reservacion = view.get_object()

        if reservacion.estado == "cancelada":
            raise PermissionDenied("No se puede modificar o cancelar una reservación que ya ha sido cancelada.")

        return func(view, request, *args, **kwargs)

    return wrapper

def verificar_usuario_pertenece_al_hotel(func):
    """
    Verifica que el usuario pertenezca al hotel asociado a la reservación o solicitud.
    """
    @wraps(func)
    def wrapper(view, request, *args, **kwargs):
        obj = view.get_object()
        usuario = request.user

        try:
            hotel = obj.reservacion.habitacion.hotel
        except AttributeError:
            # Si el objeto mismo es la reservación:
            hotel = obj.habitacion.hotel

        if usuario.rol in ["administrador", "gerente"] and EmpleadoHotel.objects.filter(usuario=usuario, hotel=hotel).exists():
            return func(view, request, *args, **kwargs)

        raise PermissionDenied("No tienes permisos para modificar este registro.")
    
    return wrapper

def verificar_recepcionista_pertenece_hotel(func):
    """
    Verifica que el usuario sea recepcionista y pertenezca al hotel de la reservación
    (útil en vistas tipo CreateAPIView donde aún no hay objeto guardado).
    """
    @wraps(func)
    def wrapper(view, serializer, *args, **kwargs):
        usuario = view.request.user
        reservacion = serializer.validated_data["reservacion"]
        hotel = reservacion.habitacion.hotel

        if usuario.rol != "recepcionista":
            raise PermissionDenied("Solo los recepcionistas pueden realizar esta acción.")

        pertenece = EmpleadoHotel.objects.filter(usuario=usuario, hotel=hotel).exists()

        if not pertenece:
            raise PermissionDenied("No perteneces al hotel relacionado con esta reservación.")

        return func(view, serializer, *args, **kwargs)

    return wrapper