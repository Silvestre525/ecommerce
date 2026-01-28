from django.urls import path

from .views import CityViewSet, CountryViewSet, ProvinceViewSet

urlpatterns = [
    # URLs esenciales para formularios de registro/checkout
    path(
        "countries/",
        CountryViewSet.as_view({"get": "public_list"}),
        name="countries_public",
    ),
    path(
        "provinces/",
        ProvinceViewSet.as_view({"get": "by_country"}),
        name="provinces_by_country",
    ),
    path(
        "cities/",
        CityViewSet.as_view({"get": "by_province"}),
        name="cities_by_province",
    ),
]
