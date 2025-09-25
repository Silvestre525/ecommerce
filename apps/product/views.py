from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from utils.permissions import IsAdministrador


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            permission_classes = [IsAdministrador]
        else:
            permission_classes = [IsAuthenticated]
        return [p() for p in permission_classes]