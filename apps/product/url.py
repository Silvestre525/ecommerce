from django.urls import path

from .views import ProductViewSet

urlpatterns = [
    path(
        "",
        ProductViewSet.as_view({"get": "list", "post": "create"}),
        name="list_administrative",
    ),
    path(
        "<int:pk>/",
        ProductViewSet.as_view(
            {"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="detail_administrative",
    ),
]