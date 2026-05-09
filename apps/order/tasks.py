from celery import shared_task
import time

@shared_task
def send_mails_confirm(orden_id, email_usuario):
    print(f"Preparando email y PDF para la orden {orden_id}...")

    time.sleep(5)

    print(f"Email enviado conexito {email_usuario}")

    return "Email procesado"
