from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Usuario
from .serializers import UsuarioSerializer
from .factories import UsuarioFactory

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        datos = serializer.validated_data
        UsuarioFactory.crear_usuario(
            username=datos["username"],
            email=datos["email"],
            password=datos["password"],
            rol=datos["rol"]
        )
