from django.conf import settings
from django.db import models

from ..BaseModel.models import BaseModel
from ..geo.models import City, Country, Province


# Create your models here.
class Person(BaseModel):
    id = models.AutoField(primary_key=True, db_column="id_person")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="person"
    )  ##Relacion con usuario ed uno a uno, usando el user  que trae django por defecto
    name = models.CharField("name", max_length=150, null=False, blank=False)
    last_name = models.CharField("last_name", max_length=150, null=False, blank=False)
    dni = models.CharField("dni", max_length=40, null=False, blank=False)

    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="persons", default=1
    )

    class Meta:
        db_table = "person"

    def __str__(self):
        return f"{self.name} {self.last_name}".strip() or str(self.user)
