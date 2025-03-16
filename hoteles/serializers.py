from rest_framework import serializers
from .models import Hotel, Habitacion

class HotelSerializer(serializers.ModelSerializer):
    propietario = serializers.ReadOnlyField(source='propietario.id')
    class Meta:
        model = Hotel
        fields = '__all__'

class HabitacionSerializer(serializers.ModelSerializer):
    hotel = serializers.ReadOnlyField(source='hotel.id') 
    class Meta:
        model = Habitacion
        fields = '__all__'
