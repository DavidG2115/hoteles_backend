from django.db import models
from usuarios.models import Usuario


class Hotel(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.TextField()
    telefono = models.CharField(max_length=15)
    propietario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="hoteles")

    def __str__(self):
        return self.nombre

class Habitacion(models.Model):
    TIPOS_HABITACION = (
        ('individual', 'Individual'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
        ('familiar', 'Familiar'),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="habitaciones")
    numero = models.CharField(max_length=10)  # Número de habitación
    tipo = models.CharField(max_length=20, choices=TIPOS_HABITACION)
    costo_por_noche = models.DecimalField(max_digits=10, decimal_places=2)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Habitación {self.numero} - {self.hotel.nombre}"
