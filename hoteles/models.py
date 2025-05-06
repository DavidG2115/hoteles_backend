from django.db import models
from usuarios.models import Usuario

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField()
    phone = models.CharField(max_length=15)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="hotels")

    def __str__(self):
        return self.name

class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()

    def __str__(self):
        return f"Image for {self.hotel.name}"


class Habitacion(models.Model):
    ROOM_TYPES = (
        ('individual', 'Individual'),
        ('doble', 'Doble'),
        ('suite', 'Suite'),
        ('familiar', 'Familiar'),
    )

    CLEANING_STATUS = (
        ("dirty", "Dirty"),
        ("cleaning", "Cleaning"),
        ("clean", "Clean"),
    )

    MAINTENANCE_STATUS = (
        ("operational", "Operational"),
        ("under_maintenance", "Under Maintenance"),
        ("maintenance_done", "Maintenance Done"),
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    number = models.CharField(max_length=10)
    type = models.CharField(max_length=20, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    cleaning_status = models.CharField(max_length=20, choices=CLEANING_STATUS, default="dirty")
    maintenance_status = models.CharField(max_length=30, choices=MAINTENANCE_STATUS, default="operational")

    # Nuevos campos
    title = models.CharField(max_length=255, default="Standard Room")
    size = models.CharField(max_length=50, blank=True)
    beds = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    view = models.CharField(max_length=100, blank=True)
    policies = models.TextField(blank=True)

    # Se manejarán relaciones separadas para services, bathroom items e imágenes
    def __str__(self):
        return f"Room {self.number} - {self.hotel.name}"


class RoomService(models.Model):
    room = models.ForeignKey(Habitacion, related_name='services', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class BathroomItem(models.Model):
    room = models.ForeignKey(Habitacion, related_name='bathroom', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)


class RoomImage(models.Model):
    room = models.ForeignKey(Habitacion, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField()
