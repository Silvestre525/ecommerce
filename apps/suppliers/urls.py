from django.urls import path

from .views import SuppliersViewSet

urlpatterns = [
    # URLs básicas CRUD
    path(
        "",
        SuppliersViewSet.as_view({"get": "list", "post": "create"}),
        name="suppliers_list_create",
    ),
    path(
        "<int:pk>/",
        SuppliersViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="suppliers_detail",
    ),
]
