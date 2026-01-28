from django.urls import path

from .views import CategoryViewSet

urlpatterns = [
    # URLs básicas CRUD
    path(
        "",
        CategoryViewSet.as_view({"get": "list", "post": "create"}),
        name="category_list_create",
    ),
    path(
        "<int:pk>/",
        CategoryViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="category_detail",
    ),
    # URL pública para lista de categorías
    path(
        "public_list/",
        CategoryViewSet.as_view({"get": "public_list"}),
        name="category_public_list",
    ),
]
