from rest_framework import serializers
from .models import Reservacion, SolicitudModificacionReservacion

class ReservacionSerializer(serializers.ModelSerializer):
    nombre_cliente = serializers.CharField(required=False, allow_blank=True)
    email_cliente = serializers.EmailField(required=False, allow_blank=True)

    class Meta:
        model = Reservacion
        fields = '__all__'
        read_only_fields = ['folio', 'estado', 'usuario']

    def validate(self, data):
        usuario = self.context['request'].user

        if not usuario.is_authenticated:
            if not data.get('nombre_cliente') or not data.get('email_cliente'):
                raise serializers.ValidationError({
                    "nombre_cliente": "Este campo es obligatorio.",
                    "email_cliente": "Este campo es obligatorio."
                })

        return data

    def create(self, validated_data):
        usuario = self.context['request'].user

        if usuario.is_authenticated:
            if not validated_data.get('nombre_cliente'):
                validated_data['nombre_cliente'] = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username

            if not validated_data.get('email_cliente'):
                validated_data['email_cliente'] = usuario.email

        return super().create(validated_data)


class SolicitudModificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudModificacionReservacion
        fields = '__all__'
        read_only_fields = ['fecha_solicitud', 'solicitante']