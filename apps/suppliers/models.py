from django.db import models

class Suppliers(models.Model):
    id = models.Autofield(primary_key=True)
    comany_name = models.CharField(max_length=50, null=False, blank=False)
    contact_person= models.CharField(max_length=50, null=False, blank=False)
    contact_email = models.EmailField(max_length=200, null=False, blamk=False)
    adress = models.CharField(max_length=100, null=False, blank=False)
    Country = models.CharField(max_length=50,null=False, blank=False)