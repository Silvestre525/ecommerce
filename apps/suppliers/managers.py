from django.db import models

class SuppliersQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
        
    def with_details(self):
        return self.select_related("city")

class SuppliersManager(models.Manager.from_queryset(SuppliersQuerySet)):
    pass
