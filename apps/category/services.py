import logging
from .models import Category

logger = logging.getLogger(__name__)

class CategoryService:
    """
    Servicio para manejar la lógica de negocio de Categorías
    """
    @staticmethod
    def get_public_list():
        return Category.objects.active().values("id", "name", "description")
