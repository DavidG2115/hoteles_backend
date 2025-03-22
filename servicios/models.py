from django.db import models
from hoteles.models import Hotel
from reservaciones.models import Reservacion

class Servicio(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="servicios")
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} - {self.hotel.nombre}"

class ReservacionServicio(models.Model):
    reservacion = models.ForeignKey(Reservacion, on_delete=models.CASCADE, related_name="servicios")
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.servicio.nombre} x{self.cantidad} - {self.reservacion.folio}"
