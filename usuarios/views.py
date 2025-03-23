from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Usuario
from .serializers import UsuarioSerializer
from django.contrib.auth.models import User
from .permissions import EsAdministrador 

class RegistroUsuarioView(generics.CreateAPIView):
    """
    View para registrar nuevos usuarios.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

class PerfilUsuarioView(APIView):
    """
    View para obtener el perfil del usuario autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)
    
# 🔹 Listar todos los usuarios (Solo administradores)
class ListarUsuariosView(generics.ListAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]  # 🔹 Solo autenticados pueden ver esto

    def get_queryset(self):
        # Solo los administradores pueden ver la lista de usuarios
        if self.request.user.rol == "administrador":
            return Usuario.objects.all()
        return Usuario.objects.none()  # No devuelve nada si no es admin
    
# 🔹 Editar un usuario (Solo administradores pueden modificar cualquier usuario)
class EditarUsuarioView(generics.UpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]  # 🔹 Solo autenticados

    def get_queryset(self):
        # Solo los administradores pueden modificar otros usuarios
        if self.request.user.rol == "administrador":
            return Usuario.objects.all()
        return Usuario.objects.none()  # No devuelve nada si no es admin
    
    
#Eliminacion de usuarios Solo Admin
class EliminarUsuarioView(generics.DestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]  # Solo admins lo controlarán en el método

    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()

        # Solo admins pueden eliminar usuarios
        if request.user.rol != "administrador":
            return Response(
                {"detail": "No tienes permisos para eliminar usuarios."},
                status=status.HTTP_403_FORBIDDEN
            )

        usuario.delete()
        return Response({"mensaje": "Usuario eliminado correctamente."}, status=status.HTTP_200_OK)