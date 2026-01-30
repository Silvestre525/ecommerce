from django.db import models


class ProductManager(models.Manager):
    """
    Manager personalizado para el modelo Product
    """

    def get_available_products(self):
        """Devuelve productos disponibles (activos y con stock)"""
        return self.filter(is_active=True, stock__gt=0)

    def get_low_stock_products(self, threshold=10):
        """Devuelve productos con stock bajo"""
        return self.filter(is_active=True, stock__lt=threshold, stock__gt=0)

    def get_out_of_stock_products(self):
        """Devuelve productos sin stock"""
        return self.filter(is_active=True, stock=0)
