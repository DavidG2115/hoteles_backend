from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Reservacion, SolicitudModificacionReservacion

# 🔸 Al crear una reservación
@receiver(post_save, sender=Reservacion)
def enviar_email_nueva_reservacion(sender, instance, created, **kwargs):
    if not created:
        return

    subject = "Reserva Recibida - Hoteles de Morelia"
    from_email = "noreply@hoteles.com"
    to = [instance.email_cliente]

    # Contexto con datos dinámicos
    context = {
        "tipo_correo": "creacion",
        "nombre": instance.nombre_cliente,
        "folio": instance.folio,
        "fecha_inicio": instance.fecha_inicio,
        "fecha_fin": instance.fecha_fin,
        "estado": instance.estado,
        "habitacion": instance.habitacion,
        "total": instance.habitacion.costo_por_noche * (instance.fecha_fin - instance.fecha_inicio).days,
        "url_gestion_reservacion": f"https://hotelmorelia.com/reservaciones/{instance.folio}/gestionar",
    }

    html_content = render_to_string("emails/reservacion.html", context)
    text_content = f"Gracias por tu reservación, {instance.nombre_cliente}. Folio: {instance.folio}"

    msg = EmailMultiAlternatives(subject, text_content, from_email, to)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# 🔸 Al modificar una reservación
@receiver(post_save, sender=Reservacion)
def enviar_email_actualizacion_reservacion(sender, instance, created, **kwargs):
    if created:
        return

    # Verificar si el guardado proviene de una solicitud aprobada
    if hasattr(instance, "_desde_solicitud_aprobada") and instance._desde_solicitud_aprobada:
        # Eliminar la bandera para evitar efectos secundarios
        del instance._desde_solicitud_aprobada
        return

    context = {
        "tipo_correo": "actualizacion",
        "nombre": instance.nombre_cliente,
        "folio": instance.folio,
        "fecha_inicio": instance.fecha_inicio,
        "fecha_fin": instance.fecha_fin,
        "estado": instance.estado,
        "habitacion": instance.habitacion,
        "url_gestion_reservacion": f"https://hotelmorelia.com/reservaciones/{instance.folio}/gestionar",
    }

    html_content = render_to_string("emails/reservacion.html", context)
    text_content = f"Tu reservación con folio {instance.folio} ha cambiado al estado: {instance.estado}."

    msg = EmailMultiAlternatives("Actualización de Reservación", text_content, "noreply@hoteles.com", [instance.email_cliente])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    
# 🔸 Al aprobar una solicitud de modificación 
@receiver(post_save, sender=SolicitudModificacionReservacion)
def enviar_email_resultado_solicitud(sender, instance, created, **kwargs):
    if created or instance.estado == "pendiente":
        return

    reservacion = instance.reservacion

    # Si fue aprobada, actualizar la reservación
    if instance.estado == "aprobada":
        reservacion._desde_solicitud_aprobada = True

        if instance.tipo == "eliminacion":
            reservacion.estado = "cancelada"
            reservacion.habitacion.disponible = True
            reservacion.habitacion.save()
            tipo_correo = "cancelacion"
            subject = "Cancelación de Reservación"
            text_content = f"Tu reservación con folio {reservacion.folio} ha sido cancelada."
        elif instance.tipo == "modificacion":
            reservacion.estado = "modificada"
            tipo_correo = "aprobacion"
            subject = "Solicitud Aprobada"
            text_content = f"La solicitud sobre tu reservación {reservacion.folio} ha sido aprobada."

        reservacion.save()

    elif instance.estado == "rechazada":
        tipo_correo = "rechazada"
        subject = "Solicitud Rechazada"
        text_content = f"La solicitud sobre tu reservación {reservacion.folio} ha sido rechazada."

    else:
        return  # Por seguridad: solo permitimos estados válidos

    # Enviar correo
    context = {
        "tipo_correo": tipo_correo,
        "nombre": reservacion.nombre_cliente,
        "folio": reservacion.folio,
        "fecha_inicio": reservacion.fecha_inicio,
        "fecha_fin": reservacion.fecha_fin,
        "estado": reservacion.estado,
        "habitacion": reservacion.habitacion,
        "url_gestion_reservacion": f"https://hotelmorelia.com/solicitudes/{instance.id}/ver",
    }

    html_content = render_to_string("emails/reservacion.html", context)

    msg = EmailMultiAlternatives(
        subject,
        text_content,
        "noreply@hoteles.com",
        [reservacion.email_cliente]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
