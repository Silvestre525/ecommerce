from rest_framework import serializers

from .models import Color


class ColorSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Color"""

    class Meta:
        model = Color
        fields = ["id", "title"]
        read_only_fields = ["id"]

    def validate_title(self, value):
        """Validar que el título no esté vacío y tenga formato adecuado"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "El título del color no puede estar vacío."
            )

        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "El título debe tener al menos 2 caracteres."
            )

        return value.strip().title()  # Capitalizar primera letra


class ColorListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""

    class Meta:
        model = Color
        fields = ["id", "title"]
