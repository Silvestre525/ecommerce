from django.db import models
from ..person.models import Person

# Create your models here.
class Order(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_order')
    title = models.CharField(max_length=100,null=False, blank=False)
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='persons')

    class Meta:
        db_table = "Order"