import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..utils.permissions import IsAdministrador, IsAdministradorOrVisitante
from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de productos.

    Permite operaciones CRUD completas con diferentes niveles de permisos:
    - Administradores: Acceso completo (crear, leer, actualizar, eliminar)
    - Visitantes: Solo lectura (listar y ver detalles)
    - Público: Acceso al catálogo básico sin autenticación
    """

    serializer_class = ProductSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["categories", "suppliers", "color", "size"]
    search_fields = ["name"]
    ordering_fields = ["name", "stock"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Optimiza las consultas con select_related y prefetch_related
        """
        return (
            Product.objects.select_related("color", "size")
            .prefetch_related("categories", "suppliers")
            .filter(is_active=True)
        )

    def get_permissions(self):
        """
        Permisos básicos:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        - public_catalog: Acceso público
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["public_catalog"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdministrador]

        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Productos"],
        summary="Listar productos",
        description="Lista todos los productos activos. **Privado:** Administrador o Visitante.",
        parameters=[
            OpenApiParameter(
                name="categories",
                description="Filtrar por categoría",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="suppliers",
                description="Filtrar por proveedor",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="search", description="Buscar por nombre", required=False, type=str
            ),
            OpenApiParameter(
                name="ordering",
                description="Ordenar por 'name' o 'stock'",
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Ver detalle de producto",
        description="Obtiene detalles completos de un producto específico. **Privado:** Administrador o Visitante.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Crear nuevo producto",
        description="Crea un nuevo producto en el sistema. **Privado:** Solo Administradores.",
        request=ProductSerializer,
        responses={
            201: ProductSerializer,
            400: OpenApiResponse(description="Datos inválidos"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Actualizar producto completo",
        description="Actualiza completamente un producto existente. **Privado:** Solo Administradores.",
        request=ProductSerializer,
        responses={
            200: ProductSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Actualizar producto parcialmente",
        description="Actualiza parcialmente un producto existente. **Privado:** Solo Administradores.",
        request=ProductSerializer,
        responses={
            200: ProductSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Eliminar producto",
        description="Elimina permanentemente un producto del sistema. **Privado:** Solo Administradores.",
        responses={
            204: OpenApiResponse(description="Producto eliminado exitosamente"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Catálogo público de productos",
        description="Obtiene un catálogo básico de productos con información limitada. **Público:** Sin autenticación requerida.",
        responses={
            200: OpenApiResponse(description="Lista básica de productos públicos")
        },
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public_catalog(self, request):
        products = self.get_queryset().values("id", "name", "img", "stock")[:20]

        return Response(
            {
                "message": "Catálogo público de productos",
                "count": len(products),
                "products": list(products),
            }
        )
