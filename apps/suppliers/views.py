import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from ..utils.permissions import IsAdministrador, IsAdministradorOrVisitante
from .models import Suppliers
from .serializers import suppliersSerializer

logger = logging.getLogger(__name__)


class SuppliersViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de proveedores.

    Permite administrar proveedores del sistema:
    - Administradores: Acceso completo (crear, leer, actualizar, eliminar)
    - Visitantes: Solo lectura (listar y ver detalles)
    """

    serializer_class = suppliersSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["city"]
    search_fields = ["company_name", "contact_person", "contact_email"]
    ordering_fields = ["company_name"]
    ordering = ["company_name"]

    def get_queryset(self):
        """
        Filtra solo proveedores activos
        """
        return Suppliers.objects.select_related("city").filter(is_active=True)

    def get_permissions(self):
        """
        Permisos básicos:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        else:
            permission_classes = [IsAdministrador]

        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Proveedores"],
        summary="Listar proveedores",
        description="Lista todos los proveedores activos del sistema. **Privado:** Administrador o Visitante.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Proveedores"],
        summary="Ver detalle de proveedor",
        description="Obtiene los detalles completos de un proveedor específico. **Privado:** Administrador o Visitante.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Proveedores"],
        summary="Crear nuevo proveedor",
        description="Crea un nuevo proveedor en el sistema. **Privado:** Solo Administradores.",
        request=suppliersSerializer,
        responses={
            201: suppliersSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
        },
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Proveedores"],
        summary="Actualizar proveedor completo",
        description="Actualiza completamente un proveedor existente. **Privado:** Solo Administradores.",
        request=suppliersSerializer,
        responses={
            200: suppliersSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Proveedor no encontrado"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Proveedores"],
        summary="Actualizar proveedor parcialmente",
        description="Actualiza parcialmente un proveedor existente. **Privado:** Solo Administradores.",
        request=suppliersSerializer,
        responses={
            200: suppliersSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Proveedor no encontrado"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Proveedores"],
        summary="Eliminar proveedor",
        description="Elimina permanentemente un proveedor del sistema. **Privado:** Solo Administradores.",
        responses={
            204: OpenApiResponse(description="Proveedor eliminado exitosamente"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Proveedor no encontrado"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
