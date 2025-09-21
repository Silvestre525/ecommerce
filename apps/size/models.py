from django.db import models
from ..BaseModel.models import BaseModel
# Create your models here.
class Size(BaseModel):
    id = models.AutoField(primary_key=True, db_column='id_size')
    title = models.CharField(max_length=50, db_column='title')

    class Meta:
        db_table = 'sizes'