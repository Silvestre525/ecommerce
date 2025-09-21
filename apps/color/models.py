from django.db import models
from ..BaseModel.models import BaseModel
# Create your models here.
class Color(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_color')
    title = models.CharField(max_length=50,null=False,blank=False )

    class Meta:
        db_table = 'colors'