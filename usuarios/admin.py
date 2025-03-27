from django.contrib import admin
from .models import Usuario, EmpleadoHotel

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'is_active')
    list_filter = ('rol',)
    search_fields = ('username', 'email')

@admin.register(EmpleadoHotel)
class EmpleadoHotelAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'hotel')
    list_filter = ('hotel',)
    search_fields = ('usuario__username', 'hotel__nombre')
