from rest_framework import serializers
from .models import Reservacion

class ReservacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservacion
        fields = '__all__'
        read_only_fields = ['folio', 'estado']  # 🔹 El folio se genera automáticamente
