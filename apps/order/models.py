from django.db import models
from ..person.models import Person

# Create your models here.
class Order(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_order')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    creation_date = models.DateTimeField(auto_now_add=True)
    
    
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='orders')

    class Meta:
        db_table = "Orders"
        ordering = ['-creation_date']