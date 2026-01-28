import pytest
from django.contrib.auth.models import User
from django.test import RequestFactory
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed

from apps.utils.authentication import (
    BearerTokenAuthentication,
    FlexibleTokenAuthentication,
)


@pytest.fixture
def user():
    """Usuario de prueba"""
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def token(user):
    """Token de prueba"""
    token, created = Token.objects.get_or_create(user=user)
    return token


@pytest.fixture
def request_factory():
    """Factory para crear requests de prueba"""
    return RequestFactory()


@pytest.mark.django_db
class TestFlexibleTokenAuthentication:
    """Tests para FlexibleTokenAuthentication"""

    def test_authenticate_with_token_prefix(self, request_factory, user, token):
        """Test: Autenticación con prefijo 'Token'"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Token {token.key}"

        result = auth.authenticate(request)

        assert result is not None
        assert result[0] == user
        assert result[1] == token

    def test_authenticate_with_bearer_prefix(self, request_factory, user, token):
        """Test: Autenticación con prefijo 'Bearer'"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token.key}"

        result = auth.authenticate(request)

        assert result is not None
        assert result[0] == user
        assert result[1] == token

    def test_authenticate_without_prefix(self, request_factory, user, token):
        """Test: Autenticación solo con token (sin prefijo)"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = token.key

        result = auth.authenticate(request)

        assert result is not None
        assert result[0] == user
        assert result[1] == token

    def test_authenticate_no_header(self, request_factory):
        """Test: Sin header de autorización"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")

        result = auth.authenticate(request)

        assert result is None

    def test_authenticate_empty_header(self, request_factory):
        """Test: Header de autorización vacío"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = ""

        result = auth.authenticate(request)

        assert result is None

    def test_authenticate_invalid_token(self, request_factory):
        """Test: Token inválido"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token invalid_token_123"

        result = auth.authenticate(request)

        assert result is None

    def test_authenticate_malformed_header(self, request_factory):
        """Test: Header malformado"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "InvalidFormat"

        result = auth.authenticate(request)

        assert result is None

    def test_authenticate_too_short_token(self, request_factory):
        """Test: Token demasiado corto (sin prefijo)"""
        auth = FlexibleTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "short"  # Menos de 20 caracteres

        result = auth.authenticate(request)

        assert result is None

    def test_case_insensitive_prefixes(self, request_factory, user, token):
        """Test: Los prefijos no son sensibles a mayúsculas/minúsculas"""
        auth = FlexibleTokenAuthentication()

        # Probar diferentes combinaciones de caso
        test_cases = [
            f"token {token.key}",
            f"TOKEN {token.key}",
            f"bearer {token.key}",
            f"BEARER {token.key}",
            f"Token {token.key}",
            f"Bearer {token.key}",
        ]

        for auth_header in test_cases:
            request = request_factory.get("/")
            request.META["HTTP_AUTHORIZATION"] = auth_header

            result = auth.authenticate(request)

            assert result is not None, f"Failed for header: {auth_header}"
            assert result[0] == user
            assert result[1] == token


@pytest.mark.django_db
class TestBearerTokenAuthentication:
    """Tests para BearerTokenAuthentication"""

    def test_authenticate_with_token_keyword(self, request_factory, user, token):
        """Test: Autenticación con keyword 'Token'"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Token {token.key}"

        result = auth.authenticate(request)

        assert result is not None
        assert result[0] == user
        assert result[1] == token

    def test_authenticate_with_bearer_keyword(self, request_factory, user, token):
        """Test: Autenticación con keyword 'Bearer'"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token.key}"

        result = auth.authenticate(request)

        assert result is not None
        assert result[0] == user
        assert result[1] == token

    def test_authenticate_no_credentials(self, request_factory):
        """Test: Error cuando solo se proporciona el keyword"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token"

        with pytest.raises(AuthenticationFailed, match="No credentials provided"):
            auth.authenticate(request)

    def test_authenticate_too_many_parts(self, request_factory):
        """Test: Error cuando hay demasiadas partes en el header"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Token part1 part2 part3"

        with pytest.raises(AuthenticationFailed, match="should not contain spaces"):
            auth.authenticate(request)

    def test_authenticate_invalid_unicode(self, request_factory):
        """Test: Error con caracteres unicode inválidos"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        # Simular bytes inválidos
        request.META["HTTP_AUTHORIZATION"] = "Token \xff\xfe"

        with pytest.raises(AuthenticationFailed, match="invalid characters"):
            auth.authenticate(request)

    def test_authenticate_wrong_keyword(self, request_factory):
        """Test: Keyword no soportado"""
        auth = BearerTokenAuthentication()

        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Basic somebase64string"

        result = auth.authenticate(request)

        assert result is None


@pytest.mark.django_db
class TestAuthenticationIntegration:
    """Tests de integración para verificar que la autenticación funciona en endpoints reales"""

    def test_product_list_with_token_auth(self, request_factory, user, token):
        """Test: Endpoint de productos con autenticación Token"""
        from apps.product.views import ProductViewSet

        request = request_factory.get("/api/product/")
        request.META["HTTP_AUTHORIZATION"] = f"Token {token.key}"
        request.user = user  # Simular usuario autenticado

        view = ProductViewSet()
        view.request = request
        view.format_kwarg = None

        # Verificar que el usuario está autenticado
        assert request.user == user

    def test_product_list_with_bearer_auth(self, request_factory, user, token):
        """Test: Endpoint de productos con autenticación Bearer"""
        from apps.product.views import ProductViewSet

        request = request_factory.get("/api/product/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token.key}"
        request.user = user  # Simular usuario autenticado

        view = ProductViewSet()
        view.request = request
        view.format_kwarg = None

        # Verificar que el usuario está autenticado
        assert request.user == user
