from django.urls import path
from .views import CatgeryViewSet

urlpatterns = [
    path("",CatgeryViewSet.as_view({"get":"list","post":"create"}),
         name="list_administrative"),
    path("<int:pk>/",CatgeryViewSet.as_view({"get":"retrieve","put":"update","delete":"destroy"}),
         name="detail_administrative"),
]