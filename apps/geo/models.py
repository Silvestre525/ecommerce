from django.db import models

class Country(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_country')
    name = models.CharField(max_length=50, null=False, blank=False)

    class Meta:
        db_table = 'Country'

    def __str__(self):
        return self.name

class Province(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_province')
    name = models.CharField(max_length=50, null=False, blank=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, db_column='province_country', related_name='provinces')

    class Meta:
        db_table = 'Province'

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class City(models.Model):
    id = models.AutoField(primary_key=True, db_column='id_city')
    name = models.CharField(max_length=50, null=False, blank=False)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, db_column='city_province', related_name='cities')

    class Meta:
        db_table = 'City'

    def __str__(self):
        return f"{self.name}, {self.province.name}, {self.province.country.name}"
