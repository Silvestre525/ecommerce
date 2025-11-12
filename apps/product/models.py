from django.db import models
from ..category.models import Category
from ..suppliers.models import Suppliers
from ..order.models import Order
from ..color.models import Color
from ..size.models import Size
from ..BaseModel.models import BaseModel
# Create your models here.
class Product(BaseModel):
    id = models.AutoField(primary_key=True,db_column='id_product')
    name = models.CharField(max_length=50, null=True)
    stock = models.IntegerField()
    img = models.CharField(max_length=100,null=True,blank=True)

    categories = models.ManyToManyField(Category, related_name='products')

    suppliers = models.ManyToManyField(Suppliers, related_name='products')
    
    order = models.ManyToManyField(Order,related_name='products')

    color = models.ForeignKey(Color, on_delete=models.CASCADE, default=1)
    size = models.ForeignKey(Size, on_delete=models.CASCADE, default=1)
    
    class Meta:
        db_table = 'Product'