from django.db import models
from hoteles.models import Hotel, Habitacion
from usuarios.models import Usuario
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



class SolicitudModificacionReservacion(models.Model):
    TIPO_SOLICITUD = [
        ('modificacion', 'Modificación'),
        ('eliminacion', 'Eliminación'),
    ]

    ESTADO_SOLICITUD = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
    ]

    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE)
    solicitante = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_SOLICITUD)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_SOLICITUD, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - {self.reservacion.folio} ({self.estado})"