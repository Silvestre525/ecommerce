from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["Debug"],
    summary="Verificar autenticación",
    description="Endpoint para verificar que la autenticación funciona correctamente con Token y Bearer.",
    responses={
        200: {
            "description": "Autenticación exitosa",
            "examples": {
                "application/json": {
                    "authenticated": True,
                    "user": {
                        "id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "groups": ["Visitante"],
                    },
                    "auth_method": "Token",
                    "message": "Autenticación exitosa",
                }
            },
        },
        401: {
            "description": "No autenticado",
            "examples": {
                "application/json": {
                    "detail": "Authentication credentials were not provided."
                }
            },
        },
    },
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def debug_auth(request):
    """
    Endpoint para verificar que la autenticación funciona correctamente.

    Útil para debugging de problemas de autenticación con diferentes clientes HTTP.
    Soporta tanto 'Token' como 'Bearer' en el header Authorization.

    Headers soportados:
    - Authorization: Token <your_token>
    - Authorization: Bearer <your_token>
    """

    # Obtener información del usuario
    user_data = {
        "id": request.user.id,
        "username": request.user.username,
        "email": request.user.email,
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "is_staff": request.user.is_staff,
        "is_active": request.user.is_active,
        "groups": list(request.user.groups.values_list("name", flat=True)),
        "date_joined": request.user.date_joined,
    }

    # Determinar el método de autenticación usado
    auth_header = request.META.get("HTTP_AUTHORIZATION", "")
    auth_method = "Unknown"

    if auth_header.startswith("Token "):
        auth_method = "Token"
    elif auth_header.startswith("Bearer "):
        auth_method = "Bearer"
    elif auth_header and not auth_header.startswith(("Token ", "Bearer ")):
        auth_method = "Token (sin prefijo)"

    # Información adicional del request
    request_info = {
        "method": request.method,
        "path": request.path,
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "remote_addr": request.META.get("REMOTE_ADDR", ""),
        "auth_header_present": bool(auth_header),
        "auth_header_format": auth_method,
    }

    # Verificar si el usuario tiene perfil de persona
    person_info = None
    if hasattr(request.user, "person"):
        try:
            person = request.user.person
            person_info = {
                "id": person.id,
                "name": person.name,
                "last_name": person.last_name,
                "dni": person.dni,
                "city": person.city.name if person.city else None,
            }
        except:
            person_info = {"error": "Error al obtener información de persona"}

    return Response(
        {
            "authenticated": True,
            "message": "✅ Autenticación exitosa",
            "auth_method": auth_method,
            "user": user_data,
            "person": person_info,
            "request_info": request_info,
            "tips": {
                "token_format": "Authorization: Token <your_token>",
                "bearer_format": "Authorization: Bearer <your_token>",
                "note": "Ambos formatos son soportados por este sistema",
            },
        },
        status=status.HTTP_200_OK,
    )


@extend_schema(
    tags=["Debug"],
    summary="Información pública del sistema",
    description="Endpoint público que no requiere autenticación para verificar conectividad.",
    responses={
        200: {
            "description": "Información del sistema",
            "examples": {
                "application/json": {
                    "system": "Ecommerce API",
                    "version": "1.0.0",
                    "status": "active",
                    "authentication_supported": ["Token", "Bearer"],
                }
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([])
def system_info(request):
    """
    Endpoint público para verificar que el sistema está funcionando.
    No requiere autenticación.
    """
    return Response(
        {
            "system": "Ecommerce API",
            "version": "1.0.0",
            "status": "🟢 Active",
            "message": "Sistema funcionando correctamente",
            "authentication": {
                "supported_methods": ["Token", "Bearer"],
                "endpoints": {
                    "public": [
                        "/api/product/public_catalog/",
                        "/api/debug/system-info/",
                    ],
                    "authenticated": [
                        "/api/product/",
                        "/api/order/",
                        "/api/debug/auth/",
                    ],
                    "admin_only": [
                        "/api/product/low_stock/",
                        "/api/product/out_of_stock/",
                    ],
                },
            },
            "documentation": "/api/docs/",
            "test_users": {
                "admin": {"username": "admin", "password": "admin123"},
                "visitor": {"username": "visitor", "password": "visitor123"},
            },
        }
    )
