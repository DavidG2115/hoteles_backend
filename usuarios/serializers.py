from rest_framework import serializers
from .models import Usuario, EmpleadoHotel
from hoteles.models import Hotel

# 🔹 Serializer para crear/editar usuarios
class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'rol']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        usuario = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            rol=validated_data['rol']
        )
        usuario.set_password(validated_data['password'])
        usuario.save()
        return usuario

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        return super().update(instance, validated_data)

# 🔹 Serializer para asignar empleados a un hotel
class AsignarEmpleadoSerializer(serializers.Serializer):
    usuario_id = serializers.IntegerField()

    def validate_usuario_id(self, value):
        try:
            usuario = Usuario.objects.get(id=value)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El usuario no existe.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        usuario_id = validated_data["usuario_id"]

        usuario = Usuario.objects.get(id=usuario_id)
        hotel = Hotel.objects.get(propietario=request.user)

        empleado, creado = EmpleadoHotel.objects.get_or_create(usuario=usuario, hotel=hotel)
        return empleado
