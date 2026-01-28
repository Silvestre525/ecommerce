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
from .serializers import (
    ProductCreateUpdateSerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductPublicSerializer,
    ProductSerializer,
)

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión completa de productos con serializers optimizados.

    Permite operaciones CRUD completas con diferentes niveles de permisos:
    - Administradores: Acceso completo (crear, leer, actualizar, eliminar)
    - Visitantes: Solo lectura (listar y ver detalles)
    - Público: Acceso al catálogo básico sin autenticación
    """

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["categories", "suppliers", "color", "size", "is_active"]
    search_fields = ["name", "color__title", "size__title"]
    ordering_fields = ["name", "stock", "creation_date", "update_date"]
    ordering = ["name"]

    def get_queryset(self):
        """
        Optimiza las consultas con select_related y prefetch_related
        """
        base_queryset = (
            Product.objects.select_related("color", "size")
            .prefetch_related("categories", "suppliers")
            .filter(is_active=True)
        )

        # Para admin, mostrar todos los productos (incluso inactivos)
        if (
            self.request.user.is_authenticated
            and self.request.user.groups.filter(name="Administrador").exists()
        ):
            return Product.objects.select_related("color", "size").prefetch_related(
                "categories", "suppliers"
            )

        return base_queryset

    def get_serializer_class(self):
        """
        Devuelve diferentes serializers según la acción
        """
        if self.action == "list":
            return ProductListSerializer
        elif self.action == "retrieve":
            return ProductDetailSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return ProductCreateUpdateSerializer
        elif self.action == "public_catalog":
            return ProductPublicSerializer
        return ProductSerializer

    def get_permissions(self):
        """
        Permisos básicos:
        - create, update, partial_update, destroy: Solo Administradores
        - list, retrieve: Administradores y Visitantes
        - public_catalog, low_stock, out_of_stock: Según configuración específica
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            permission_classes = [IsAdministrador]
        elif self.action in ["list", "retrieve"]:
            permission_classes = [IsAdministradorOrVisitante]
        elif self.action in ["public_catalog"]:
            permission_classes = [AllowAny]
        elif self.action in ["low_stock", "out_of_stock", "toggle_status"]:
            permission_classes = [IsAdministrador]
        else:
            permission_classes = [IsAdministrador]

        return [permission() for permission in permission_classes]

    @extend_schema(
        tags=["Productos"],
        summary="Listar productos",
        description="Lista todos los productos activos con información optimizada. **Privado:** Administrador o Visitante.",
        parameters=[
            OpenApiParameter(
                name="categories",
                description="Filtrar por categoría (ID)",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="suppliers",
                description="Filtrar por proveedor (ID)",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="color",
                description="Filtrar por color (ID)",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="size",
                description="Filtrar por tamaño (ID)",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="search",
                description="Buscar por nombre, color o tamaño",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Ordenar por 'name', 'stock', 'creation_date'",
                required=False,
                type=str,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Agregar estadísticas útiles
        queryset = self.filter_queryset(self.get_queryset())
        total_stock = sum(product.stock for product in queryset)
        low_stock_count = len([p for p in queryset if p.is_low_stock])

        if isinstance(response.data, dict) and "results" in response.data:
            response.data.update(
                {
                    "statistics": {
                        "total_products": queryset.count(),
                        "total_stock": total_stock,
                        "low_stock_products": low_stock_count,
                    }
                }
            )

        return response

    @extend_schema(
        tags=["Productos"],
        summary="Ver detalle de producto",
        description="Obtiene detalles completos de un producto específico con información extendida. **Privado:** Administrador o Visitante.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Crear nuevo producto",
        description="Crea un nuevo producto en el sistema con validaciones mejoradas. **Privado:** Solo Administradores.",
        request=ProductCreateUpdateSerializer,
        responses={
            201: ProductDetailSerializer,
            400: OpenApiResponse(description="Datos inválidos"),
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
        },
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            logger.info(f"Producto creado: {product.name} por {request.user.username}")

            # Devolver respuesta con serializer detallado
            detail_serializer = ProductDetailSerializer(product)
            return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Productos"],
        summary="Actualizar producto completo",
        description="Actualiza completamente un producto existente. **Privado:** Solo Administradores.",
        request=ProductCreateUpdateSerializer,
        responses={
            200: ProductDetailSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            logger.info(
                f"Producto actualizado: {product.name} por {request.user.username}"
            )

            # Devolver respuesta con serializer detallado
            detail_serializer = ProductDetailSerializer(product)
            return Response(detail_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=["Productos"],
        summary="Actualizar producto parcialmente",
        description="Actualiza parcialmente un producto existente. **Privado:** Solo Administradores.",
        request=ProductCreateUpdateSerializer,
        responses={
            200: ProductDetailSerializer,
            403: OpenApiResponse(description="Sin permisos - solo administradores"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            logger.info(
                f"Producto actualizado parcialmente: {product.name} por {request.user.username}"
            )

            # Devolver respuesta con serializer detallado
            detail_serializer = ProductDetailSerializer(product)
            return Response(detail_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        instance = self.get_object()
        product_name = instance.name
        logger.warning(
            f"Producto eliminado: {product_name} por {request.user.username}"
        )
        return super().destroy(request, *args, **kwargs)

    @extend_schema(
        tags=["Productos"],
        summary="Catálogo público de productos",
        description="Obtiene un catálogo básico de productos disponibles con información mínima. **Público:** Sin autenticación requerida.",
        responses={
            200: OpenApiResponse(description="Lista básica de productos públicos")
        },
    )
    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def public_catalog(self, request):
        products = Product.get_available_products()[:20]
        serializer = ProductPublicSerializer(products, many=True)

        return Response(
            {
                "message": "Catálogo público de productos",
                "count": len(products),
                "products": serializer.data,
            }
        )

    @extend_schema(
        tags=["Productos"],
        summary="Productos con stock bajo",
        description="Lista productos con stock bajo (menos de 10 unidades). **Privado:** Solo Administradores.",
        parameters=[
            OpenApiParameter(
                name="threshold",
                description="Umbral de stock bajo (por defecto 10)",
                required=False,
                type=int,
            ),
        ],
        responses={
            200: OpenApiResponse(description="Lista de productos con stock bajo")
        },
    )
    @action(detail=False, methods=["get"])
    def low_stock(self, request):
        threshold = int(request.query_params.get("threshold", 10))
        products = Product.get_low_stock_products(threshold)
        serializer = ProductListSerializer(products, many=True)

        return Response(
            {
                "message": f"Productos con stock bajo (menos de {threshold} unidades)",
                "threshold": threshold,
                "count": products.count(),
                "products": serializer.data,
            }
        )

    @extend_schema(
        tags=["Productos"],
        summary="Productos sin stock",
        description="Lista productos sin stock disponible. **Privado:** Solo Administradores.",
        responses={200: OpenApiResponse(description="Lista de productos sin stock")},
    )
    @action(detail=False, methods=["get"])
    def out_of_stock(self, request):
        products = Product.get_out_of_stock_products()
        serializer = ProductListSerializer(products, many=True)

        return Response(
            {
                "message": "Productos sin stock",
                "count": products.count(),
                "products": serializer.data,
            }
        )

    @extend_schema(
        tags=["Productos"],
        summary="Cambiar estado activo/inactivo",
        description="Activa o desactiva un producto. **Privado:** Solo Administradores.",
        responses={
            200: OpenApiResponse(description="Estado cambiado exitosamente"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    @action(detail=True, methods=["patch"])
    def toggle_status(self, request, pk=None):
        product = self.get_object()

        if product.is_active:
            product.deactivate()
            message = f"Producto '{product.name}' desactivado"
        else:
            product.activate()
            message = f"Producto '{product.name}' activado"

        logger.info(f"{message} por {request.user.username}")

        serializer = ProductDetailSerializer(product)
        return Response(
            {
                "message": message,
                "product": serializer.data,
            }
        )

    @extend_schema(
        tags=["Productos"],
        summary="Actualizar stock",
        description="Añade o reduce stock de un producto. **Privado:** Solo Administradores.",
        request={
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "reduce"]},
                "quantity": {"type": "integer", "minimum": 1},
            },
            "required": ["action", "quantity"],
        },
        responses={
            200: OpenApiResponse(description="Stock actualizado exitosamente"),
            400: OpenApiResponse(description="Datos inválidos"),
            404: OpenApiResponse(description="Producto no encontrado"),
        },
    )
    @action(detail=True, methods=["patch"])
    def update_stock(self, request, pk=None):
        product = self.get_object()

        action = request.data.get("action")
        quantity = request.data.get("quantity")

        if not action or not quantity:
            return Response(
                {"error": "Se requieren 'action' y 'quantity'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if quantity <= 0:
            return Response(
                {"error": "La cantidad debe ser mayor a 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            if action == "add":
                new_stock = product.add_stock(quantity)
                message = f"Se añadieron {quantity} unidades"
            elif action == "reduce":
                new_stock = product.reduce_stock(quantity)
                message = f"Se redujeron {quantity} unidades"
            else:
                return Response(
                    {"error": "Acción debe ser 'add' o 'reduce'"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            logger.info(
                f"Stock actualizado para {product.name}: {message} por {request.user.username}"
            )

            serializer = ProductDetailSerializer(product)
            return Response(
                {
                    "message": message,
                    "previous_stock": new_stock - quantity
                    if action == "add"
                    else new_stock + quantity,
                    "current_stock": new_stock,
                    "product": serializer.data,
                }
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
