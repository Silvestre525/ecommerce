from django.db import models

class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

class CategoryManager(models.Manager.from_queryset(CategoryQuerySet)):
    pass
