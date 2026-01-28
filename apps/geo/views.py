import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..utils.permissions import IsAdministrador, IsAdministradorOrVisitante
from .models import City, Country, Province
from .serializers import (
    CityDetailSerializer,
    CitySerializer,
    CountryDetailSerializer,
    CountrySerializer,
    ProvinceDetailSerializer,
    ProvinceSerializer,
)

logger = logging.getLogger(__name__)


class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de países.

    **Uso principal:** Proveer datos geográficos para formularios de registro
    y direcciones de envío. La mayoría de endpoints son públicos.
    """

    queryset = Country.objects.all()
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "id"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CountryDetailSerializer
        return CountrySerializer

    def get_permissions(self):
        """
        Configuración de permisos para países:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        - public_list: Acceso público
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["public_list"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdministrador]

        logger.debug(
            f"CountryViewSet.{self.action}: Permisos {[p.__name__ for p in permission_classes]}"
        )
        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Geografía"],
        summary="Lista pública de países",
        description="Obtiene lista de todos los países disponibles para formularios. **Público:** Sin autenticación requerida.",
        responses={200: OpenApiResponse(description="Lista de países disponibles")},
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public_list(self, request):
        countries = Country.objects.values("id", "name").order_by("name")

        return Response(
            {
                "message": "Lista pública de países",
                "count": len(countries),
                "countries": list(countries),
            }
        )


class ProvinceViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de provincias/estados.

    **Uso principal:** Obtener provincias filtradas por país para
    formularios de direcciones.
    """

    queryset = Province.objects.select_related("country")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["country"]
    search_fields = ["name", "country__name"]
    ordering_fields = ["name", "country__name"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ProvinceDetailSerializer
        return ProvinceSerializer

    def get_permissions(self):
        """
        Configuración de permisos para provincias:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        - by_country: Acceso público
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["by_country"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdministrador]

        logger.debug(
            f"ProvinceViewSet.{self.action}: Permisos {[p.__name__ for p in permission_classes]}"
        )
        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Geografía"],
        summary="Obtener provincias por país",
        description="Lista las provincias de un país específico para formularios. **Público:** Sin autenticación requerida.",
        parameters=[
            OpenApiParameter(
                name="country_id", description="ID del país", required=True, type=int
            )
        ],
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def by_country(self, request):
        country_id = request.query_params.get("country_id")

        if not country_id:
            return Response(
                {"error": "Parámetro 'country_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            country = Country.objects.get(id=country_id)
            provinces = (
                Province.objects.filter(country=country)
                .values("id", "name")
                .order_by("name")
            )

            return Response(
                {
                    "country": {"id": country.id, "name": country.name},
                    "provinces": list(provinces),
                    "count": len(provinces),
                }
            )
        except Country.DoesNotExist:
            return Response(
                {"error": "País no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de ciudades.

    **Uso principal:** Obtener ciudades filtradas por provincia
    para formularios de direcciones de envío.
    """

    queryset = City.objects.select_related("province", "province__country")
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["province", "province__country"]
    search_fields = ["name", "province__name", "province__country__name"]
    ordering_fields = ["name", "province__name"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CityDetailSerializer
        return CitySerializer

    def get_permissions(self):
        """
        Configuración de permisos para ciudades:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        - by_province: Acceso público
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["by_province", "by_country"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdministrador]

        logger.debug(
            f"CityViewSet.{self.action}: Permisos {[p.__name__ for p in permission_classes]}"
        )
        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Geografía"],
        summary="Obtener ciudades por provincia",
        description="Lista las ciudades de una provincia específica para formularios. **Público:** Sin autenticación requerida.",
        parameters=[
            OpenApiParameter(
                name="province_id",
                description="ID de la provincia",
                required=True,
                type=int,
            )
        ],
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def by_province(self, request):
        province_id = request.query_params.get("province_id")

        if not province_id:
            return Response(
                {"error": "Parámetro 'province_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            province = Province.objects.select_related("country").get(id=province_id)
            cities = (
                City.objects.filter(province=province)
                .values("id", "name")
                .order_by("name")
            )

            return Response(
                {
                    "province": {
                        "id": province.id,
                        "name": province.name,
                        "country_name": province.country.name,
                    },
                    "cities": list(cities),
                    "count": len(cities),
                }
            )
        except Province.DoesNotExist:
            return Response(
                {"error": "Provincia no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def by_country(self, request):
        """
        Obtener todas las ciudades de un país (acceso público)
        """
        country_id = request.query_params.get("country_id")

        if not country_id:
            return Response(
                {"error": "Parámetro 'country_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        logger.debug(f"Consulta de ciudades por país {country_id}")

        try:
            country = Country.objects.get(id=country_id)
            cities = (
                City.objects.select_related("province")
                .filter(province__country=country)
                .values("id", "name", "province__name")
                .order_by("name")
            )

            return Response(
                {
                    "country": {"id": country.id, "name": country.name},
                    "cities": list(cities),
                    "count": len(cities),
                }
            )
        except Country.DoesNotExist:
            return Response(
                {"error": "País no encontrado"}, status=status.HTTP_404_NOT_FOUND
            )
