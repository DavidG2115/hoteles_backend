from rest_framework import serializers
from .models import Hotel, Habitacion, HotelImage, RoomImage, RoomService, BathroomItem
from usuarios.models import Usuario

# Serializador para las imágenes del hotel
class HotelImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelImage
        fields = ['id', 'image_url']


# Serializador para las imágenes de la habitación
class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImage
        fields = ['id', 'image_url']


# Serializador para los servicios de habitación
class RoomServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomService
        fields = ['id', 'name']


# Serializador para artículos de baño
class BathroomItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BathroomItem
        fields = ['id', 'name']


# Serializador de habitaciones (detallado, con imágenes, servicios y baño)
class HabitacionSerializer(serializers.ModelSerializer):
    images = RoomImageSerializer(many=True, read_only=True)
    services = RoomServiceSerializer(many=True, read_only=True)
    bathroom = BathroomItemSerializer(many=True, read_only=True)

    class Meta:
        model = Habitacion
        fields = [
            'id', 'hotel', 'number', 'title', 'size', 'beds',
            'description', 'view', 'policies', 'price_per_night',
            'available', 'cleaning_status', 'maintenance_status',
            'type', 'images', 'services', 'bathroom'
        ]


# Serializador público (para listado simple de habitaciones disponibles)
class HabitacionPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = ['id', 'title', 'price_per_night', 'available']


# Serializador de hotel con imágenes (y habitaciones si luego las quieres anidar)
class HotelSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(write_only=True, required=False)
    images = HotelImageSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'location', 'phone', 'description',
            'owner', 'owner_id', 'images',
        ]
        read_only_fields = ['owner']

    def create(self, validated_data):
        owner_id = validated_data.pop('owner_id', None)
        if owner_id:
            try:
                owner = Usuario.objects.get(id=owner_id, rol='administrador')
            except Usuario.DoesNotExist:
                raise serializers.ValidationError("The specified owner does not exist or is not an administrator.")
        else:
            owner = self.context['request'].user
        return Hotel.objects.create(owner=owner, **validated_data)


# Serializer anidado de habitaciones
class HabitacionNestedSerializer(serializers.ModelSerializer):
    services = RoomServiceSerializer(many=True, read_only=True)
    bathroom = BathroomItemSerializer(many=True, read_only=True)
    images = RoomImageSerializer(many=True, read_only=True)

    class Meta:
        model = Habitacion
        fields = [
            'id', 'title', 'size', 'beds', 'description',
            'view', 'policies', 'price_per_night', 'available',
            'cleaning_status', 'maintenance_status',
            'services', 'bathroom', 'images'
        ]


# Serializer de hotel con habitaciones anidadas
class HotelWithRoomsSerializer(serializers.ModelSerializer):
    owner_id = serializers.IntegerField(write_only=True, required=False)
    images = HotelImageSerializer(source='hotelimage_set', many=True, read_only=True)
    rooms = HabitacionNestedSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = [
            'id', 'name', 'location', 'phone', 'description',
            'owner', 'owner_id', 'images', 'rooms'
        ]
        read_only_fields = ['owner']