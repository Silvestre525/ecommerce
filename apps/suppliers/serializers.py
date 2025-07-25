from rest_framework import serializers
from .models import Suppliers


class suppliersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suppliers
        fields = '__all__'