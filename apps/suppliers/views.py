from django.shortcuts import render
from rest_framework import models
from .models import Suppliers
from .serializers import suppliersSerializer

class suppliersViewSet(models.ModelViewSet):
    queryset = Suppliers.object.all()
    serializer_class = suppliersSerializer