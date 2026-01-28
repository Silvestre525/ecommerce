from django.urls import path

from .views import ProductViewSet

urlpatterns = [
    # URLs básicas CRUD
    path(
        "",
        ProductViewSet.as_view({"get": "list", "post": "create"}),
        name="product_list_create",
    ),
    path(
        "<int:pk>/",
        ProductViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="product_detail",
    ),
    # URL pública para catálogo
    path(
        "public_catalog/",
        ProductViewSet.as_view({"get": "public_catalog"}),
        name="product_public_catalog",
    ),
]
