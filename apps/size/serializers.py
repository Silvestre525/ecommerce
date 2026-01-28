from rest_framework import serializers

from .models import Size


class SizeSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Size"""

    class Meta:
        model = Size
        fields = ["id", "title"]
        read_only_fields = ["id"]

    def validate_title(self, value):
        """Validar que el título no esté vacío y tenga formato adecuado"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "El título del tamaño no puede estar vacío."
            )

        if len(value.strip()) < 1:
            raise serializers.ValidationError(
                "El título debe tener al menos 1 carácter."
            )

        return (
            value.strip().upper()
        )  # Convertir a mayúsculas para consistencia (S, M, L, XL)


class SizeListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""

    class Meta:
        model = Size
        fields = ["id", "title"]
