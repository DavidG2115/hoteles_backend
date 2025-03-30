# reservaciones/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Reservacion, SolicitudModificacionReservacion

# 🔸 Al crear una reservación
@receiver(post_save, sender=Reservacion)
def enviar_email_nueva_reservacion(sender, instance, created, **kwargs):
    if created:
        habitacion = instance.habitacion
        hotel = habitacion.hotel

        send_mail(
            "Reserva Recibida - Hoteles de Morelia",
            f"Hola {instance.nombre_cliente},\n\n"
            f"Gracias por reservar con nosotros. Tu reservación con folio {instance.folio} está registrada como *pendiente*.\n\n"
            f"Por favor realiza el pago correspondiente y envía tu comprobante al correo del hotel para confirmar tu reservación.\n\n"
            f"Hotel: {hotel.nombre}\n"
            f"Dirección: {hotel.direccion}\n"
            f"Teléfono: {hotel.telefono}\n\n"
            f"Fecha de entrada: {instance.fecha_inicio}\n"
            f"Fecha de salida: {instance.fecha_fin}\n"
            f"Habitación: {habitacion.numero} ({habitacion.tipo})\n"
            f"Costo por noche: ${habitacion.costo_por_noche}\n"
            f"Folio: {instance.folio}\n\n"
            f"➡️ IMPORTANTE: Envía el comprobante a: contacto@hotelmorelia.com\n\n"
            f"Gracias por tu preferencia.",
            "noreply@hoteles.com",
            [instance.email_cliente],
            fail_silently=True
        )


# 🔸 Al modificar o cancelar reservación
@receiver(post_save, sender=Reservacion)
def enviar_email_actualizacion_reservacion(sender, instance, created, **kwargs):
    if not created:
        mensaje = f"Tu reservación con folio {instance.folio} ha cambiado al estado: {instance.estado}."
        send_mail(
            "Actualización de Reservación",
            mensaje,
            "noreply@hoteles.com",
            [instance.email_cliente],
            fail_silently=True
        )

# 🔸 Al aprobar solicitud de modificación o eliminación
@receiver(post_save, sender=SolicitudModificacionReservacion)
def enviar_email_aprobacion_solicitud(sender, instance, created, **kwargs):
    if not created and instance.estado == "aprobada":
        reservacion = instance.reservacion
        mensaje = f"Hola {reservacion.nombre_cliente}, la solicitud sobre tu reservación {reservacion.folio} ha sido aprobada ({instance.tipo})."
        send_mail(
            "Solicitud Aprobada",
            mensaje,
            "noreply@hoteles.com",
            [reservacion.email_cliente],
            fail_silently=True
        )
