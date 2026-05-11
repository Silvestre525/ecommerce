import logging
from .models import Order

logger = logging.getLogger(__name__)

class OrderService:
    """
    Servicio para manejar la lógica de negocio de Órdenes
    """

    @staticmethod
    def prepare_create_data(data, user):
        """
        Asigna la persona al request data si es un visitante.
        Lanza ValueError si el usuario no tiene perfil de persona.
        """
        if not user.groups.filter(name="Administrador").exists():
            try:
                person = user.person
                # Es importante asegurar que 'data' sea mutable si es un QueryDict, 
                # pero DRF request.data ya es un dict en muchos casos. 
                # La vista suele lidiar con esto copiando el request.data si es inmutable.
                data["person"] = person.id
            except Exception:
                raise ValueError("No se encontró el perfil de persona para el usuario")
        return data

    @staticmethod
    def process_after_creation(order_id, email):
        """
        Lanza la tarea de Celery para enviar el correo de confirmación.
        """
        from .tasks import send_mails_confirm
        send_mails_confirm.delay(order_id, email)

    @staticmethod
    def get_user_orders(user):
        """
        Obtiene las órdenes del usuario y un mensaje descriptivo.
        Lanza ValueError si el usuario no tiene perfil.
        """
        try:
            person = user.person
            orders = Order.objects.filter(person=person).order_by("-creation_date")
            message = f"Órdenes de {person.name} {person.last_name}"
            return orders, message
        except Exception:
            raise ValueError("No se encontró el perfil de persona para el usuario")
