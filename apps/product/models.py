from django.db import models
from ..category.models import Category
from ..suppliers.models import Suppliers
# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True,db_column='id_product')
    name = models.CharField(max_length=50, null=True)
    stock = models.IntegerField()
    img = models.CharField(max_length=100,null=True,blank=True)

    categories = models.ManyToManyField(Category, related_name='products')

    product = models.ForeignKey(Suppliers, related_name="suppliers", on_delete=models.CASCADE, null=True, blank=True) 
    
    class Meta:
        db_table = 'Product'