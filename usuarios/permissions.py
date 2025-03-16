from rest_framework.permissions import BasePermission

class EsAdministrador(BasePermission):
    """
    Permiso para permitir solo a administradores crear hoteles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "administrador"
