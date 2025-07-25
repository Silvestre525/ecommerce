import pytest
from ..serializers import ProductSerializer
from ..models import Category

@pytest.mark.django_db
def test_product_serializer_valid():
    category = Category.objects.create(name="Deportes")

    data = {
        "name": "zapatillasNike",
        "stock": 4,
        "categories": [category.id],
    }

    serializer = ProductSerializer(data=data)

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["name"] == "zapatillasNike"
    assert serializer.validated_data["stock"] == 4
    
