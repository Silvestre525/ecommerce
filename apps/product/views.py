from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerilizer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serilizer_class = ProductSerilizer