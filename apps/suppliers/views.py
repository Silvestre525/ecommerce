from django.shortcuts import render
from rest_framework import viewsets
from .models import Suppliers
from .serializers import suppliersSerializer

class suppliersViewSet(viewsets.ModelViewSet):
    queryset = Suppliers.objects.all()
    serializer_class = suppliersSerializer