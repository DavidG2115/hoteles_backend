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
    hotel_id = serializers.IntegerField()

    def validate(self, data):
        usuario_id = data["usuario_id"]
        hotel_id = data["hotel_id"]
        request = self.context["request"]

        # Validar existencia del usuario
        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("El usuario no existe.")

        # Validar existencia del hotel y que le pertenezca al usuario autenticado
        try:
            hotel = Hotel.objects.get(id=hotel_id, propietario=request.user)
        except Hotel.DoesNotExist:
            raise serializers.ValidationError("No tienes permiso para asignar empleados a este hotel.")

        # Guardamos el objeto para reutilizarlo en create()
        self.usuario = usuario
        self.hotel = hotel

        return data

    def create(self, validated_data):
        empleado, creado = EmpleadoHotel.objects.get_or_create(
            usuario=self.usuario,
            hotel=self.hotel
        )
        return empleado
