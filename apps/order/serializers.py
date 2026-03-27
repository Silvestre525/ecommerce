from rest_framework import serializers
from django.db import transaction
from ..person.serializers import PersonSerializer
from ..product.models import Product
from .models import Order, DetailOrder

class DetailOrderSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetailOrder
        fields = [
            "id", 
            "product", 
            "product_name", 
            "quantity", 
            "price_at_purchase", 
            "subtotal"
        ]
        read_only_fields = ["price_at_purchase"]

class OrderSerializer(serializers.ModelSerializer):
    person_name = serializers.CharField(source="person.name", read_only=True)
    person_last_name = serializers.CharField(source="person.last_name", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "total",
            "status",
            "creation_date",
            "person",
            "person_name",
            "person_last_name",
        ]
        read_only_fields = ["id", "creation_date", "total"]

class OrderDetailSerializer(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)
    details = DetailOrderSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "total", "status", "creation_date", "person", "details"]

class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer auxiliar para recibir items en la creación"""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1)

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSerializer(many=True, write_only=True)

    class Meta:
        model = Order
        fields = ["person", "items", "total", "status"]
        read_only_fields = ["total"]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Usamos una transacción atómica para asegurar que si falla el stock, no se cree la orden
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            total = 0

            for item in items_data:
                product = item['product']
                quantity = item['quantity']
                
                # Validación de stock
                if product.stock < quantity:
                    raise serializers.ValidationError(
                        f"No hay suficiente stock para {product.name}. Disponible: {product.stock}"
                    )
                
                # Crear detalle con el precio actual del producto
                DetailOrder.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=product.price
                )
                
                # Reducir stock y sumar al total
                product.reduce_stock(quantity)
                total += product.price * quantity
            
            # Guardar el total calculado en el backend
            order.total = total
            order.save()
            
        return order
