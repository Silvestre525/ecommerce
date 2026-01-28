from django.urls import path

from .views import OrderViewSet

urlpatterns = [
    # URLs básicas CRUD
    path(
        "",
        OrderViewSet.as_view({"get": "list", "post": "create"}),
        name="order_list_create",
    ),
    path(
        "<int:pk>/",
        OrderViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="order_detail",
    ),
    # URL para que los usuarios vean sus propias órdenes
    path(
        "my_orders/",
        OrderViewSet.as_view({"get": "my_orders"}),
        name="order_my_orders",
    ),
]
