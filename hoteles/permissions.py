from rest_framework.permissions import BasePermission

class EsAdministrador(BasePermission):
    """
    Permiso para permitir solo a administradores crear hoteles.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "administrador"

class EsSuperAdmin(BasePermission):
    """
    Permite el acceso solo a superusuarios (is_superuser=True)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser
class EsJefeCamaristas(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "camarista"

class EsJefeMantenimiento(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "mantenimiento"
