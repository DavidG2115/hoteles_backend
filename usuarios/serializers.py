from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol']
        extra_kwargs = {
            'password': {'write_only': True}  # No mostrar el password en respuestas
        }

    def create(self, validated_data):
        """Crear usuario con contraseña encriptada"""
        usuario = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            rol=validated_data['rol']
        )
        usuario.set_password(validated_data['password'])  # 🔹 Encripta correctamente la contraseña
        usuario.save()
        return usuario
