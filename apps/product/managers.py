from django.db import models


class ProductQuerySet(models.QuerySet):
    """
    QuerySet personalizado para permitir encadenamiento de filtros y optimizaciones.
    """

    def get_available_products(self):
        """Devuelve productos disponibles (activos y con stock)"""
        return self.filter(is_active=True, stock__gt=0)

    def get_low_stock_products(self, threshold=10):
        """Devuelve productos con stock bajo pero mayor a 0"""
        return self.filter(is_active=True, stock__lt=threshold, stock__gt=0)

    def get_out_of_stock_products(self):
        """Devuelve productos sin stock"""
        return self.filter(is_active=True, stock=0)

    def with_details(self):
        """Aplica optimizaciones de base de datos para recuperar relaciones"""
        return self.select_related("color", "size").prefetch_related("categories", "suppliers")

    def active(self):
        """Devuelve productos activos"""
        return self.filter(is_active=True)


class ProductManager(models.Manager.from_queryset(ProductQuerySet)):
    """
    Manager personalizado para el modelo Product
    """
    pass
