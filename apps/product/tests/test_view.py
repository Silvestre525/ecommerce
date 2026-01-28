import pytest
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APIClient

from apps.category.models import Category
from apps.color.models import Color
from apps.person.models import Person
from apps.product.models import Product
from apps.size.models import Size
from apps.suppliers.models import Suppliers


@pytest.fixture
def admin_user():
    """Usuario administrador para tests"""
    user = User.objects.create_user(
        username="admin", password="test123", email="admin@test.com"
    )
    admin_group, _ = Group.objects.get_or_create(name="Administrador")
    user.groups.add(admin_group)
    return user


@pytest.fixture
def visitor_user():
    """Usuario visitante para tests"""
    user = User.objects.create_user(
        username="visitor", password="test123", email="visitor@test.com"
    )
    visitor_group, _ = Group.objects.get_or_create(name="Visitante")
    user.groups.add(visitor_group)
    # Crear perfil de persona
    Person.objects.create(user=user, name="Test", last_name="Visitor", dni="12345678")
    return user


@pytest.fixture
def api_client():
    """Cliente API para tests"""
    return APIClient()


@pytest.fixture
def sample_color():
    """Color de ejemplo para tests"""
    return Color.objects.create(title="Rojo")


@pytest.fixture
def sample_size():
    """Tamaño de ejemplo para tests"""
    return Size.objects.create(title="M")


@pytest.fixture
def sample_category():
    """Categoría de ejemplo para tests"""
    from apps.category.models import Category

    return Category.objects.create(name="Ropa")


@pytest.fixture
def sample_supplier():
    """Proveedor de ejemplo para tests"""
    return Suppliers.objects.create(name="Proveedor Test")


@pytest.fixture
def sample_product(sample_color, sample_size):
    """Producto de ejemplo para tests"""
    return Product.objects.create(
        name="Producto Test",
        stock=10,
        color=sample_color,
        size=sample_size,
        is_active=True,
    )


@pytest.mark.django_db
class TestProductAPI:
    """Tests para el API de productos"""

    def test_public_catalog_access(self, api_client, sample_product):
        """Test: El catálogo público debe ser accesible sin autenticación"""
        url = reverse("product-public-catalog")
        response = api_client.get(url)

        assert response.status_code == 200
        assert "products" in response.data
        assert response.data["count"] >= 1

    def test_list_products_admin(self, api_client, admin_user, sample_product):
        """Test: Admin puede ver todos los productos"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == 200
        # La respuesta puede ser una lista directa o paginada
        if isinstance(response.data, list):
            assert len(response.data) >= 1
        else:
            assert "results" in response.data or "count" in response.data

    def test_list_products_visitor(self, api_client, visitor_user, sample_product):
        """Test: Visitante puede ver productos activos"""
        api_client.force_authenticate(user=visitor_user)
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == 200
        # La respuesta puede ser una lista directa o paginada
        if isinstance(response.data, list):
            assert len(response.data) >= 1
        else:
            assert "results" in response.data or "count" in response.data

    def test_list_products_unauthenticated(self, api_client, sample_product):
        """Test: Usuario sin autenticar no puede acceder al listado completo"""
        url = reverse("product-list")
        response = api_client.get(url)

        assert response.status_code == 401

    def test_retrieve_product_admin(self, api_client, admin_user, sample_product):
        """Test: Admin puede ver detalles de producto"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-detail", kwargs={"pk": sample_product.id})
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["id"] == sample_product.id
        assert "color" in response.data
        assert "size" in response.data

    def test_create_product_admin(
        self, api_client, admin_user, sample_color, sample_size
    ):
        """Test: Admin puede crear productos"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        product_data = {
            "name": "Nuevo Producto",
            "stock": 5,
            "color": sample_color.id,
            "size": sample_size.id,
        }

        response = api_client.post(url, product_data, format="json")

        assert response.status_code == 201
        assert response.data["name"] == "Nuevo Producto"
        assert Product.objects.filter(name="Nuevo Producto").exists()

    def test_create_product_visitor_forbidden(
        self, api_client, visitor_user, sample_color, sample_size
    ):
        """Test: Visitante no puede crear productos"""
        api_client.force_authenticate(user=visitor_user)
        url = reverse("product-list")

        product_data = {
            "name": "Nuevo Producto",
            "stock": 5,
            "color": sample_color.id,
            "size": sample_size.id,
        }

        response = api_client.post(url, product_data, format="json")

        assert response.status_code == 403

    def test_update_product_admin(self, api_client, admin_user, sample_product):
        """Test: Admin puede actualizar productos"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-detail", kwargs={"pk": sample_product.id})

        update_data = {
            "name": "Producto Actualizado",
            "stock": 15,
            "color": sample_product.color.id,
            "size": sample_product.size.id,
        }

        response = api_client.put(url, update_data, format="json")

        assert response.status_code == 200
        assert response.data["name"] == "Producto Actualizado"

        # Verificar en base de datos
        sample_product.refresh_from_db()
        assert sample_product.name == "Producto Actualizado"

    def test_partial_update_product_admin(self, api_client, admin_user, sample_product):
        """Test: Admin puede hacer actualizaciones parciales"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-detail", kwargs={"pk": sample_product.id})

        update_data = {"stock": 20}

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == 200
        assert response.data["stock"] == 20

        # Verificar en base de datos
        sample_product.refresh_from_db()
        assert sample_product.stock == 20

    def test_delete_product_admin(self, api_client, admin_user, sample_product):
        """Test: Admin puede eliminar productos"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-detail", kwargs={"pk": sample_product.id})

        response = api_client.delete(url)

        assert response.status_code == 204
        assert not Product.objects.filter(id=sample_product.id).exists()

    def test_delete_product_visitor_forbidden(
        self, api_client, visitor_user, sample_product
    ):
        """Test: Visitante no puede eliminar productos"""
        api_client.force_authenticate(user=visitor_user)
        url = reverse("product-detail", kwargs={"pk": sample_product.id})

        response = api_client.delete(url)

        assert response.status_code == 403

    def test_low_stock_products(
        self, api_client, admin_user, sample_color, sample_size
    ):
        """Test: Endpoint de productos con stock bajo"""
        # Crear productos con stock bajo
        Product.objects.create(
            name="Stock Bajo 1", stock=5, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="Stock Bajo 2", stock=2, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="Stock Alto", stock=50, color=sample_color, size=sample_size
        )

        api_client.force_authenticate(user=admin_user)
        url = reverse("product-low-stock")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] >= 2
        assert "products" in response.data

    def test_out_of_stock_products(
        self, api_client, admin_user, sample_color, sample_size
    ):
        """Test: Endpoint de productos sin stock"""
        # Crear productos sin stock
        Product.objects.create(
            name="Sin Stock 1", stock=0, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="Sin Stock 2", stock=0, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="Con Stock", stock=10, color=sample_color, size=sample_size
        )

        api_client.force_authenticate(user=admin_user)
        url = reverse("product-out-of-stock")
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] >= 2
        assert "products" in response.data

    def test_toggle_product_status(self, api_client, admin_user, sample_product):
        """Test: Cambiar estado activo/inactivo de producto"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-toggle-status", kwargs={"pk": sample_product.id})

        # El producto inicialmente está activo
        assert sample_product.is_active is True

        # Desactivar
        response = api_client.patch(url)
        assert response.status_code == 200

        sample_product.refresh_from_db()
        assert sample_product.is_active is False

        # Activar nuevamente
        response = api_client.patch(url)
        assert response.status_code == 200

        sample_product.refresh_from_db()
        assert sample_product.is_active is True

    def test_update_stock_add(self, api_client, admin_user, sample_product):
        """Test: Añadir stock a producto"""
        initial_stock = sample_product.stock
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-update-stock", kwargs={"pk": sample_product.id})

        stock_data = {"action": "add", "quantity": 5}

        response = api_client.patch(url, stock_data, format="json")

        assert response.status_code == 200
        assert response.data["current_stock"] == initial_stock + 5

        sample_product.refresh_from_db()
        assert sample_product.stock == initial_stock + 5

    def test_update_stock_reduce(self, api_client, admin_user, sample_product):
        """Test: Reducir stock de producto"""
        initial_stock = sample_product.stock
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-update-stock", kwargs={"pk": sample_product.id})

        stock_data = {"action": "reduce", "quantity": 3}

        response = api_client.patch(url, stock_data, format="json")

        assert response.status_code == 200
        assert response.data["current_stock"] == initial_stock - 3

        sample_product.refresh_from_db()
        assert sample_product.stock == initial_stock - 3

    def test_update_stock_insufficient(self, api_client, admin_user):
        """Test: Error al reducir más stock del disponible"""
        product = Product.objects.create(
            name="Producto Stock Bajo",
            stock=2,
            color=Color.objects.create(title="Azul"),
            size=Size.objects.create(title="L"),
        )

        api_client.force_authenticate(user=admin_user)
        url = reverse("product-update-stock", kwargs={"pk": product.id})

        stock_data = {
            "action": "reduce",
            "quantity": 5,  # Más de lo disponible
        }

        response = api_client.patch(url, stock_data, format="json")

        assert response.status_code == 400
        assert "error" in response.data

    def test_product_validation_empty_name(
        self, api_client, admin_user, sample_color, sample_size
    ):
        """Test: Validación de nombre vacío"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        product_data = {
            "name": "",
            "stock": 5,
            "color": sample_color.id,
            "size": sample_size.id,
        }

        response = api_client.post(url, product_data, format="json")

        assert response.status_code == 400
        assert "name" in response.data

    def test_product_validation_negative_stock(
        self, api_client, admin_user, sample_color, sample_size
    ):
        """Test: Validación de stock negativo"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        product_data = {
            "name": "Producto Test",
            "stock": -5,
            "color": sample_color.id,
            "size": sample_size.id,
        }

        response = api_client.post(url, product_data, format="json")

        assert response.status_code == 400
        assert "stock" in response.data

    def test_product_search(self, api_client, admin_user, sample_color, sample_size):
        """Test: Búsqueda de productos"""
        Product.objects.create(
            name="Camiseta Roja", stock=10, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="Pantalón Azul", stock=15, color=sample_color, size=sample_size
        )

        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        # Buscar por nombre
        response = api_client.get(url, {"search": "Camiseta"})

        assert response.status_code == 200
        # Verificar según el formato de respuesta
        if isinstance(response.data, list):
            products = response.data
        else:
            products = response.data.get("results", response.data)

        assert len(products) >= 1
        assert any("Camiseta" in product["name"] for product in products)

    def test_product_filtering(self, api_client, admin_user, sample_product):
        """Test: Filtrado de productos"""
        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        # Filtrar por color
        response = api_client.get(url, {"color": sample_product.color.id})

        assert response.status_code == 200
        # Verificar según el formato de respuesta
        if isinstance(response.data, list):
            assert len(response.data) >= 1
        else:
            results = response.data.get("results", response.data)
            assert len(results) >= 1

    def test_product_ordering(self, api_client, admin_user, sample_color, sample_size):
        """Test: Ordenación de productos"""
        Product.objects.create(
            name="Z Producto", stock=5, color=sample_color, size=sample_size
        )
        Product.objects.create(
            name="A Producto", stock=15, color=sample_color, size=sample_size
        )

        api_client.force_authenticate(user=admin_user)
        url = reverse("product-list")

        # Ordenar por nombre ascendente
        response = api_client.get(url, {"ordering": "name"})

        assert response.status_code == 200
        # Obtener productos según el formato de respuesta
        if isinstance(response.data, list):
            products = response.data
        else:
            products = response.data.get("results", response.data)

        if len(products) >= 2:
            assert products[0]["name"] <= products[1]["name"]


@pytest.mark.django_db
class TestProductModel:
    """Tests para el modelo Product"""

    def test_product_creation(self, sample_color, sample_size):
        """Test: Creación básica de producto"""
        product = Product.objects.create(
            name="Producto Test", stock=10, color=sample_color, size=sample_size
        )

        assert product.name == "Producto Test"
        assert product.stock == 10
        assert product.is_active is True
        assert product.is_available is True

    def test_product_str_representation(self, sample_product):
        """Test: Representación string del producto"""
        str_repr = str(sample_product)
        assert sample_product.name in str_repr
        assert str(sample_product.stock) in str_repr

    def test_product_properties(self, sample_color, sample_size):
        """Test: Propiedades del producto"""
        # Producto con stock bajo
        low_stock_product = Product.objects.create(
            name="Stock Bajo", stock=5, color=sample_color, size=sample_size
        )

        assert low_stock_product.is_low_stock is True
        assert low_stock_product.stock_status == "Stock bajo"

        # Producto sin stock
        no_stock_product = Product.objects.create(
            name="Sin Stock", stock=0, color=sample_color, size=sample_size
        )

        assert no_stock_product.is_available is False
        assert no_stock_product.stock_status == "Sin stock"

    def test_product_add_stock(self, sample_product):
        """Test: Añadir stock al producto"""
        initial_stock = sample_product.stock
        new_stock = sample_product.add_stock(5)

        assert new_stock == initial_stock + 5
        assert sample_product.stock == initial_stock + 5

    def test_product_reduce_stock(self, sample_product):
        """Test: Reducir stock del producto"""
        initial_stock = sample_product.stock
        new_stock = sample_product.reduce_stock(3)

        assert new_stock == initial_stock - 3
        assert sample_product.stock == initial_stock - 3

    def test_product_reduce_stock_insufficient(self, sample_product):
        """Test: Error al reducir más stock del disponible"""
        with pytest.raises(ValueError, match="No hay suficiente stock disponible"):
            sample_product.reduce_stock(sample_product.stock + 1)

    def test_product_activate_deactivate(self, sample_product):
        """Test: Activar y desactivar producto"""
        # Desactivar
        sample_product.deactivate()
        assert sample_product.is_active is False

        # Activar
        sample_product.activate()
        assert sample_product.is_active is True

    def test_product_class_methods(self, sample_color, sample_size):
        """Test: Métodos de clase del producto"""
        # Crear productos de prueba
        Product.objects.create(
            name="Disponible",
            stock=10,
            color=sample_color,
            size=sample_size,
            is_active=True,
        )
        Product.objects.create(
            name="Stock Bajo",
            stock=5,
            color=sample_color,
            size=sample_size,
            is_active=True,
        )
        Product.objects.create(
            name="Sin Stock",
            stock=0,
            color=sample_color,
            size=sample_size,
            is_active=True,
        )
        Product.objects.create(
            name="Inactivo",
            stock=10,
            color=sample_color,
            size=sample_size,
            is_active=False,
        )

        # Testear métodos de clase
        available = Product.get_available_products()
        low_stock = Product.get_low_stock_products()
        out_of_stock = Product.get_out_of_stock_products()

        assert available.count() >= 1
        assert low_stock.count() >= 1
        assert out_of_stock.count() >= 1
