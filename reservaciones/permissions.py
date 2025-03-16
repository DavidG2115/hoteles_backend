from rest_framework.permissions import BasePermission

class EsAdministradorOGerente(BasePermission):
    """
    Permiso para permitir solo a administradores y gerentes modificar o cancelar reservaciones.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol in ["administrador", "gerente"]
