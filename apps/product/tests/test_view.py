import pytest
from rest_framework.test import APIClient
from ..models import Product

@pytest.mark.django_db
def test_list_product():
    Product.objects.create(id = 1, name = "zapatillas", stock = 2)
    Product.objects.create(id = 2, name = "zapatillas2", stock = 6)
    Product.objects.create(id = 3, name = "zapatillas3", stock = 7)
    Product.objects.create(id = 4, name = "zapatillas4", stock = 8)

    client = APIClient()
    response = client.get("/api/product/")

    assert response.status_code == 200
    assert len(response.data) == 4