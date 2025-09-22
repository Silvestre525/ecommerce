from django.db import models
from ..BaseModel.models import BaseModel
from ..geo.models import Country, Province, City
class Suppliers(BaseModel):
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=50, null=False, blank=False)
    contact_person= models.CharField(max_length=50, null=False, blank=False)
    contact_email = models.EmailField(max_length=200, null=False, blank=False)
    adress = models.CharField(max_length=100, null=False, blank=False)

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='suppliers',default=1)
  

    class Meta:
        db_table = "Suppliers"

    def __str__(self):
        return self.company_name
    