from rest_framework import serializers
from .models import Reservacion, SolicitudModificacionReservacion

class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = '__all__'
        read_only_fields = ['folio', 'estado']  # 🔹 El folio se genera automáticamente

class SolicitudModificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudModificacionReservacion
        fields = '__all__'
        read_only_fields = ['fecha_solicitud', 'solicitante']