from django.apps import AppConfig


class ReservacionesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reservaciones'
    
    def ready(self):
        import reservaciones.signals
