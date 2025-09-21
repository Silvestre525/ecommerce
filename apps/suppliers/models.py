from django.db import models
from ..BaseModel.models import BaseModel

class Suppliers(BaseModel):
    id = models.AutoField(primary_key=True)
    comany_name = models.CharField(max_length=50, null=False, blank=False)
    contact_person= models.CharField(max_length=50, null=False, blank=False)
    contact_email = models.EmailField(max_length=200, null=False, blank=False)
    adress = models.CharField(max_length=100, null=False, blank=False)
  

    class Meta:
        db_table = "Suppliers"

    