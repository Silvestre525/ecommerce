from rest_framework import serilizers
from models import Product

class ProductSerilizer(serilizers.ModelSerilizer):
    class Meta:
        model = Product
        fields = ['all']