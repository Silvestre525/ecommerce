import pytest
from rest_framework.test import APIClient
from ..models import Product

@pytest.mark.django_db
def test_list_product():
    Product.objects.create(id = 1, name = "zapatillas", stock = 2)

    client = APIClient()
    response = client.get("/api/product/")

    assert response.status_code == 200
    assert len(response.data) == 1