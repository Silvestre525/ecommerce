from django.contrib.auth import authenticate
from django.shortcuts import render
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    UserLoginSerializer,
    UserRegistrationSerializer,
)
from .services import AuthService, PersonService


class LoginView(APIView):
    """
    Vista para autenticación de usuarios existentes.

    Permite a usuarios registrados obtener un token de autenticación
    para acceder a endpoints protegidos de la API.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Autenticación"],
        summary="Iniciar sesión",
        description="Autentica a un usuario y devuelve un token de acceso. **Público:** Sin autenticación requerida.",
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(description="Login exitoso - Token generado"),
            400: OpenApiResponse(description="Datos inválidos"),
            401: OpenApiResponse(description="Credenciales incorrectas"),
        },
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            try:
                user, token = AuthService.authenticate_user(username, password)
                return Response(
                    {
                        "token": token.key,
                        "user_id": user.pk,
                        "username": user.username,
                        "message": "Login successful",
                    },
                    status=status.HTTP_200_OK,
                )
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
            except PermissionError as e:
                return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    Vista para registro de nuevos usuarios.

    Permite crear nuevas cuentas de usuario con perfil de persona asociado.
    Los nuevos usuarios se asignan automáticamente al grupo "Visitante".
    """

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Autenticación"],
        summary="Registrar nuevo usuario",
        description="Crea una nueva cuenta de usuario con perfil de persona y asigna rol de Visitante. **Público:** Sin autenticación requerida.",
        request=UserRegistrationSerializer,
        responses={
            201: OpenApiResponse(description="Usuario creado exitosamente"),
            400: OpenApiResponse(description="Datos inválidos o usuario ya existe"),
        },
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user, token = AuthService.register_user(serializer)
            return Response(
                {"token": token.key, "user_id": user.pk, "username": user.username},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    Vista para consultar el perfil del usuario autenticado.

    Permite ver información personal y de cuenta del usuario actual.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Autenticación"],
        summary="Ver perfil de usuario",
        description="Obtiene la información completa del perfil del usuario autenticado. **Privado:** Usuario autenticado (cualquier rol).",
        responses={
            200: OpenApiResponse(description="Información del perfil"),
            401: OpenApiResponse(description="Token inválido o faltante"),
        },
    )
    def get(self, request):
        data = PersonService.get_profile_data(request.user)
        return Response(data)
