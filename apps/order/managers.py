from django.db import models

class OrderQuerySet(models.QuerySet):
    """
    QuerySet personalizado para Order
    """

    def for_user(self, user):
        """
        Filtra órdenes según el rol del usuario:
        - Admin: todas las órdenes
        - Visitante: solo sus órdenes
        """
        if user.groups.filter(name="Administrador").exists():
            return self.all()
        try:
            return self.filter(person__user=user)
        except Exception:
            return self.none()

    def with_details(self):
        """
        Optimiza consultas trayendo relaciones comunes
        """
        return self.select_related("person", "person__user")


class OrderManager(models.Manager.from_queryset(OrderQuerySet)):
    """Manager que extiende de OrderQuerySet"""
    pass
