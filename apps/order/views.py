import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..utils.permissions import (
    IsAdministrador,
    IsAdministradorOrVisitante,
    IsOwnerOrAdministrador,
)
from .models import Order
from .serializers import OrderCreateSerializer, OrderDetailSerializer, OrderSerializer

logger = logging.getLogger(__name__)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de órdenes/pedidos.

    Sistema de permisos inteligente:
    - Administradores: Pueden ver y gestionar todas las órdenes
    - Visitantes: Solo pueden ver y gestionar sus propias órdenes
    - Propietarios: Solo pueden acceder a sus órdenes específicas
    """

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["person"]
    search_fields = ["person__name", "person__last_name"]
    ordering_fields = ["creation_date", "total"]
    ordering = ["-creation_date"]

    def get_queryset(self):
        """
        Filtra órdenes según el usuario
        """
        queryset = Order.objects.select_related("person", "person__user")

        # Si es administrador, puede ver todas las órdenes
        if self.request.user.groups.filter(name="Administrador").exists():
            return queryset

        # Si es visitante, solo puede ver sus propias órdenes
        try:
            return queryset.filter(person__user=self.request.user)
        except:
            return Order.objects.none()

    def get_serializer_class(self):
        """
        Devuelve diferentes serializers según la acción
        """
        if self.action == "create":
            return OrderCreateSerializer
        elif self.action == "retrieve":
            return OrderDetailSerializer
        return OrderSerializer

    def get_permissions(self):
        """
        Permisos básicos:
        - create: Administradores y Visitantes
        - update, partial_update, retrieve: Solo propietario o Administrador
        - destroy: Solo Administradores
        - list: Administradores (todas) o Visitantes (solo suyas)
        - my_orders: Visitantes autenticados
        """
        if self.action == "create":
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["update", "partial_update", "retrieve"]:
            permission_classes = [IsOwnerOrAdministrador]
        elif self.action == "destroy":
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "my_orders"]:
            permission_classes = [IsAdministradorOrVisitante]
        else:
            permission_classes = [IsAdministrador]

        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Órdenes"],
        summary="Listar órdenes",
        description="Lista órdenes del sistema. Administradores ven todas, Visitantes solo las suyas. **Privado:** Administrador o Visitante.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Ver detalle de orden",
        description="Obtiene los detalles completos de una orden específica. **Privado:** Propietario o Administrador.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Crear nueva orden",
        description="Crea una nueva orden en el sistema. **Privado:** Administrador o Visitante.",
        request=OrderCreateSerializer,
        responses={
            201: OrderCreateSerializer,
            400: OpenApiResponse(description="Datos inválidos"),
        },
    )
    def create(self, request, *args, **kwargs):
        # Si es visitante, asignar automáticamente su persona
        if not request.user.groups.filter(name="Administrador").exists():
            try:
                person = request.user.person
                request.data["person"] = person.id
            except:
                return Response(
                    {"error": "No se encontró el perfil de persona para el usuario"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Actualizar orden completa",
        description="Actualiza completamente una orden existente. **Privado:** Propietario o Administrador.",
        request=OrderCreateSerializer,
        responses={
            200: OrderCreateSerializer,
            403: OpenApiResponse(
                description="Sin permisos - solo propietario o administrador"
            ),
            404: OpenApiResponse(description="Orden no encontrada"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Actualizar orden parcialmente",
        description="Actualiza parcialmente una orden existente. **Privado:** Propietario o Administrador.",
        request=OrderCreateSerializer,
        responses={
            200: OrderCreateSerializer,
            403: OpenApiResponse(
                description="Sin permisos - solo propietario o administrador"
            ),
            404: OpenApiResponse(description="Orden no encontrada"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Eliminar orden",
        description="Elimina permanentemente una orden del sistema. **Privado:** Solo Administradores.",
        responses={
            204: OpenApiResponse(description="Orden eliminada exitosamente"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Orden no encontrada"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Órdenes"],
        summary="Mis órdenes",
        description="Obtiene todas las órdenes del usuario actual. **Privado:** Administrador o Visitante.",
        responses={
            200: OpenApiResponse(description="Lista de órdenes del usuario"),
            400: OpenApiResponse(description="Error al obtener perfil de usuario"),
        },
    )
    @action(
        detail=False, methods=["get"], permission_classes=[IsAdministradorOrVisitante]
    )
    def my_orders(self, request):
        try:
            person = request.user.person
            orders = Order.objects.filter(person=person).order_by("-creation_date")
            serializer = OrderSerializer(orders, many=True)

            return Response(
                {
                    "message": f"Órdenes de {person.name} {person.last_name}",
                    "count": orders.count(),
                    "orders": serializer.data,
                }
            )
        except:
            return Response(
                {"error": "No se encontró el perfil de persona para el usuario"},
                status=status.HTTP_400_BAD_REQUEST,
            )
