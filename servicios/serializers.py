from rest_framework import serializers
from .models import Servicio, ReservacionServicio

class ServicioSerializer(serializers.ModelSerializer):
    hotel = serializers.ReadOnlyField(source='hotel.id')  # Se asigna automáticamente

    class Meta:
        model = Servicio
        fields = '__all__'

class ReservacionServicioSerializer(serializers.ModelSerializer):
    reservacion = serializers.ReadOnlyField(source='reservacion.folio') 
    class Meta:
        model = ReservacionServicio
        fields = '__all__'
