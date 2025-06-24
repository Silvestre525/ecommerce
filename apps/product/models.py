from django.db import models

# Create your models here.
class Product(models.Model):
    id = models.AutoField(primary_key=True,db_column='id_product')
    name = models.CharField(max_length=50, null=True)
    stock = models.IntegerField()
    img = models.CharField(max_length=100,null=True,blank=True)
    
    class Meta:
        db_table = 'Product'