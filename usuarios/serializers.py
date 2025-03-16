from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol']
        extra_kwargs = {'password': {'write_only': True}}  # Para que no se muestre en respuestas

    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        usuario = Usuario.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            rol=validated_data['rol']
        )
        usuario.set_password(validated_data['password'])  # Hash de la contraseña
        usuario.save()
        return usuario
