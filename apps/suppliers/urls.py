from django.urls import path
from .views import suppliersViewSet

urlpatterns = [
    path("",suppliersViewSet.as_view({"get":"list","post":"create"})),
    path("<int:pk>/",suppliersViewSet.as_view({"put":"update","delete":"destroy"}))
]