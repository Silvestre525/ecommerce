from rest_framework import serializers

from ..person.serializers import PersonSerializer
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.name", read_only=True)
    person_last_name = serializers.CharField(source="person.last_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total",
            "creation_date",
            "person",
            "person_name",
            "person_last_name",
        ]
        read_only_fields = ["id", "creation_date"]


class OrderDetailSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "total", "creation_date", "person", "products"]
        read_only_fields = ["id", "creation_date"]

    def get_products(self, obj):
        from ..product.serializers import ProductSerializer

        return ProductSerializer(obj.products.filter(is_active=True), many=True).data


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["total", "person"]

    def validate_total(self, value):
        if value < 0:
            raise serializers.ValidationError("El total no puede ser negativo")
        return value
