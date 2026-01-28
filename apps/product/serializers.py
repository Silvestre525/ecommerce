from rest_framework import serializers

from ..color.serializers import ColorSerializer
from ..size.serializers import SizeSerializer
from .models import Product


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listado de productos"""

    color_name = serializers.CharField(source="color.title", read_only=True)
    size_name = serializers.CharField(source="size.title", read_only=True)
    total_categories = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "stock",
            "img",
            "color_name",
            "size_name",
            "total_categories",
            "is_low_stock",
            "creation_date",
        ]

    def get_total_categories(self, obj):
        return obj.categories.count()

    def get_is_low_stock(self, obj):
        return obj.stock < 10


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de producto"""

    color = ColorSerializer(read_only=True)
    size = SizeSerializer(read_only=True)
    categories = serializers.StringRelatedField(many=True, read_only=True)
    suppliers = serializers.StringRelatedField(many=True, read_only=True)
    is_available = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "stock",
            "img",
            "creation_date",
            "update_date",
            "color",
            "size",
            "categories",
            "suppliers",
            "is_available",
            "is_low_stock",
            "stock_status",
        ]

    def get_is_available(self, obj):
        return obj.stock > 0

    def get_is_low_stock(self, obj):
        return obj.stock < 10

    def get_stock_status(self, obj):
        if obj.stock == 0:
            return "Sin stock"
        elif obj.stock < 10:
            return "Stock bajo"
        elif obj.stock < 50:
            return "Stock normal"
        else:
            return "Stock alto"


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar productos"""

    class Meta:
        model = Product
        fields = ["name", "stock", "img", "categories", "suppliers", "color", "size"]

    def validate_name(self, value):
        """Validar que el nombre no esté vacío y tenga longitud adecuada"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "El nombre del producto no puede estar vacío."
            )

        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El nombre debe tener al menos 2 caracteres."
            )

        return value.strip().title()  # Capitalizar primera letra de cada palabra

    def validate_stock(self, value):
        """Validar que el stock sea un número positivo"""
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")

        return value

    def validate_img(self, value):
        """Validar formato de imagen si se proporciona"""
        if value:
            # Validaciones básicas de URL de imagen
            valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
            if not any(value.lower().endswith(ext) for ext in valid_extensions):
                raise serializers.ValidationError(
                    "La URL de imagen debe terminar en .jpg, .jpeg, .png, .gif o .webp"
                )
        return value

    def validate(self, attrs):
        """Validaciones a nivel de objeto"""
        # Validar que si no hay stock, no esté en muchas categorías
        if attrs.get("stock", 0) == 0 and len(attrs.get("categories", [])) > 3:
            raise serializers.ValidationError(
                "Un producto sin stock no debería estar en más de 3 categorías."
            )

        return attrs

    def create(self, validated_data):
        """Crear producto con manejo de relaciones many-to-many"""
        categories = validated_data.pop("categories", [])
        suppliers = validated_data.pop("suppliers", [])

        product = Product(**validated_data)
        product.save()

        if categories:
            product.categories.set(categories)
        if suppliers:
            product.suppliers.set(suppliers)

        return product

    def update(self, instance, validated_data):
        """Actualizar producto con manejo de relaciones many-to-many"""
        categories = validated_data.pop("categories", None)
        suppliers = validated_data.pop("suppliers", None)

        # Actualizar campos simples
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar relaciones many-to-many si se proporcionan
        if categories is not None:
            instance.categories.set(categories)
        if suppliers is not None:
            instance.suppliers.set(suppliers)

        return instance


class ProductPublicSerializer(serializers.ModelSerializer):
    """Serializer minimalista para catálogo público"""

    stock_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "img", "stock_available"]

    def get_stock_available(self, obj):
        """Solo indica si hay stock disponible, no la cantidad exacta"""
        return obj.stock > 0


# Serializer principal que delega a los específicos
class ProductSerializer(ProductCreateUpdateSerializer):
    """
    Serializer principal que mantiene compatibilidad con código existente
    pero usa las mejores prácticas implementadas en ProductCreateUpdateSerializer
    """

    pass
