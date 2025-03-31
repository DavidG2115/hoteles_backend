from rest_framework import generics, status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Usuario, EmpleadoHotel
from .serializers import UsuarioSerializer, AsignarEmpleadoSerializer
from .permissions import EsAdministradorOGerenteDelHotel, EsAdministrador

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
    permission_classes = [IsAuthenticated, EsAdministrador]  # 🔹 Solo autenticados pueden ver esto

    
# 🔹 Editar un usuario (Solo administradores pueden modificar cualquier usuario)
class EditarUsuarioView(generics.UpdateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, EsAdministrador]  # 🔹 Solo autenticados

    
    
#Eliminacion de usuarios Solo Admin
class EliminarUsuarioView(generics.DestroyAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated, EsAdministrador]  # Solo admins lo controlarán en el método

    
class AsignarEmpleadoView(APIView):
    permission_classes = [IsAuthenticated, EsAdministradorOGerenteDelHotel]  # Usar el permiso personalizado

    def post(self, request):
        serializer = AsignarEmpleadoSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        empleado = serializer.save()
        return Response(
            {"mensaje": f"{empleado.usuario.username} asignado al hotel {empleado.hotel.nombre} correctamente."},
            status=status.HTTP_201_CREATED
        )
    
# 
class DesasignarEmpleadoView(APIView):
    permission_classes = [IsAuthenticated, EsAdministrador]  # Usar el permiso personalizado

    def post(self, request):
        usuario_id = request.data.get("usuario_id")
        hotel_id = request.data.get("hotel_id")

        if not usuario_id or not hotel_id:
            return Response(
                {"detail": "Se requieren los campos usuario_id y hotel_id."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar la relación y eliminarla
        try:
            empleado = EmpleadoHotel.objects.get(usuario_id=usuario_id, hotel_id=hotel_id)
        except EmpleadoHotel.DoesNotExist:
            return Response(
                {"detail": "Este usuario no está asignado a ese hotel."},
                status=status.HTTP_404_NOT_FOUND
            )

        empleado.delete()
        return Response({"mensaje": "Empleado desasignado correctamente."}, status=status.HTTP_204_NO_CONTENT)