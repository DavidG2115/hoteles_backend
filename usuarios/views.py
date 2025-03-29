from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Usuario, EmpleadoHotel
from .serializers import UsuarioSerializer, AsignarEmpleadoSerializer
from django.contrib.auth.models import User
from .permissions import EsAdministrador, PerteneceAlHotel
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
    permission_classes = [permissions.IsAuthenticated]  # Ya validas dentro de la vista

    def post(self, request):
        usuario_id = request.data.get("usuario_id")
        hotel_id = request.data.get("hotel_id")

        if not usuario_id or not hotel_id:
            return Response(
                {"detail": "Se requieren los campos usuario_id y hotel_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar que el hotel le pertenezca al usuario autenticado
        try:
            hotel = Hotel.objects.get(id=hotel_id, propietario=request.user)
        except Hotel.DoesNotExist:
            return Response(
                {"detail": "No tienes permiso para modificar este hotel."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Buscar la relación y eliminarla
        try:
            empleado = EmpleadoHotel.objects.get(usuario_id=usuario_id, hotel=hotel)
        except EmpleadoHotel.DoesNotExist:
            return Response(
                {"detail": "Este usuario no está asignado a ese hotel."},
                status=status.HTTP_404_NOT_FOUND
            )

        empleado.delete()
        return Response({"mensaje": "Empleado desasignado correctamente."}, status=status.HTTP_204_NO_CONTENT)