from rest_framework import serializers
from .models import Hotel, Habitacion
from usuarios.models import Usuario

class HotelSerializer(serializers.ModelSerializer):
    propietario_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Hotel
        fields = ['id', 'nombre', 'direccion', 'telefono', 'propietario', 'propietario_id']
        read_only_fields = ['propietario']

    def create(self, validated_data):
        propietario_id = validated_data.pop('propietario_id', None)

        if propietario_id:
            try:
                propietario = Usuario.objects.get(id=propietario_id, rol='administrador')
            except Usuario.DoesNotExist:
                raise serializers.ValidationError("El propietario especificado no existe o no es administrador.")
        else:
            propietario = self.context['request'].user  # Por defecto, quien hace la petición

        return Hotel.objects.create(propietario=propietario, **validated_data)

class HabitacionSerializer(serializers.ModelSerializer):
    hotel = serializers.ReadOnlyField(source='hotel.id') 
    class Meta:
        model = Habitacion
        fields = '__all__'

class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = "__all__"


class HabitacionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ["id", "numero", "tipo", "costo_por_noche", "disponible"]
