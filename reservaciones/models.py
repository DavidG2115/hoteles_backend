from django.db import models
from hoteles.models import Hotel, Habitacion
import uuid

class Reservacion(models.Model):
    ESTADO_RESERVA = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    )

    folio = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    nombre_cliente = models.CharField(max_length=255)
    email_cliente = models.EmailField()
    habitacion = models.ForeignKey(Habitacion, on_delete=models.CASCADE, related_name="reservaciones")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA, default='pendiente')

    def __str__(self):
        return f"Reservación {self.folio} - {self.estado}"
