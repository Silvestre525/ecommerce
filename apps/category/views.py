import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..utils.permissions import IsAdministrador, IsAdministradorOrVisitante
from .models import Category
from .serializers import CategorySerializer

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de categorías de productos.

    Permite organizar productos por categorías con diferentes niveles de permisos:
    - Administradores: Acceso completo (crear, leer, actualizar, eliminar)
    - Visitantes: Solo lectura (listar y ver detalles)
    - Público: Acceso a lista básica sin autenticación
    """

    serializer_class = CategorySerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Filtra solo categorías activas
        """
        return Category.objects.filter(is_active=True)

    def get_permissions(self):
        """
        Permisos básicos:
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

        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Categorías"],
        summary="Listar categorías",
        description="Lista todas las categorías activas del sistema. **Privado:** Administrador o Visitante.",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Buscar por nombre o descripción",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Ordenar por nombre",
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Ver detalle de categoría",
        description="Obtiene los detalles completos de una categoría específica. **Privado:** Administrador o Visitante.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Crear nueva categoría",
        description="Crea una nueva categoría en el sistema. **Privado:** Solo Administradores.",
        request=CategorySerializer,
        responses={
            201: CategorySerializer,
            400: OpenApiResponse(description="Datos inválidos"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Actualizar categoría completa",
        description="Actualiza completamente una categoría existente. **Privado:** Solo Administradores.",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Categoría no encontrada"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Actualizar categoría parcialmente",
        description="Actualiza parcialmente una categoría existente. **Privado:** Solo Administradores.",
        request=CategorySerializer,
        responses={
            200: CategorySerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Categoría no encontrada"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Eliminar categoría",
        description="Elimina permanentemente una categoría del sistema. **Privado:** Solo Administradores.",
        responses={
            204: OpenApiResponse(description="Categoría eliminada exitosamente"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Categoría no encontrada"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Categorías"],
        summary="Lista pública de categorías",
        description="Obtiene una lista básica de categorías para navegación y filtros. **Público:** Sin autenticación requerida.",
        responses={
            200: OpenApiResponse(description="Lista básica de categorías públicas")
        },
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public_list(self, request):
        categories = self.get_queryset().values("id", "name", "description")

        return Response(
            {
                "message": "Lista pública de categorías",
                "count": len(categories),
                "categories": list(categories),
            }
        )
