from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('gerente', 'Gerente'),
        ('camarista', 'Camarista'),
        ('mantenimiento', 'Mantenimiento'),
        ('cliente', 'Cliente'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    
    # Configurar el campo de autenticación principal
    USERNAME_FIELD = 'username'  # Django autenticará con username

    # Evitar conflictos con el modelo auth.User de Django
    groups = models.ManyToManyField(Group, related_name="usuario_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="usuario_permissions", blank=True)

    def __str__(self):
        return f"{self.username} - {self.rol}"

class EmpleadoHotel(models.Model):
    usuario = models.ForeignKey("usuarios.Usuario", on_delete=models.CASCADE)
    hotel = models.ForeignKey("hoteles.Hotel", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('usuario', 'hotel')

    def __str__(self):
        return f"{self.usuario.username} trabaja en {self.hotel.nombre}"
