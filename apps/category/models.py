from django.db import models
from ..BaseModel.models import BaseModel
# Create your models here.
class Category(BaseModel):
    id = models.AutoField(primary_key=True,db_column='id_category')
    name = models.CharField(max_length=50,null=True, blank=True)
    description = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "Category"