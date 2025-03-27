from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Usuario, EmpleadoHotel
from .serializers import UsuarioSerializer, AsignarEmpleadoSerializer
from django.contrib.auth.models import User
from .permissions import EsAdministrador 
from hoteles.models import Hotel

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
    
class AsignarEmpleadoView(APIView):
    permission_classes = [EsAdministrador]  # O puedes crear un permiso tipo EsAdministradorDeHotel

    def post(self, request):
        serializer = AsignarEmpleadoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        empleado = serializer.save()
        return Response({"mensaje": f"{empleado.usuario.username} asignado al hotel {empleado.hotel.nombre} correctamente."})
    
class DesasignarEmpleadoView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        usuario_id = request.data.get("usuario_id")

        if not usuario_id:
            return Response({"error": "Falta el campo usuario_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response({"error": "El usuario no existe."}, status=status.HTTP_404_NOT_FOUND)

        try:
            hotel = Hotel.objects.get(propietario=request.user)
            relacion = EmpleadoHotel.objects.get(usuario=usuario, hotel=hotel)
            relacion.delete()
            return Response({"mensaje": f"{usuario.username} ha sido desasignado del hotel {hotel.nombre}."})
        except Hotel.DoesNotExist:
            return Response({"error": "No se encontró un hotel asociado al administrador."}, status=status.HTTP_404_NOT_FOUND)
        except EmpleadoHotel.DoesNotExist:
            return Response({"error": "Este usuario no está asignado a tu hotel."}, status=status.HTTP_400_BAD_REQUEST)
