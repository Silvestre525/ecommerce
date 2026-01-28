import logging

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class BearerTokenAuthentication(TokenAuthentication):
    """
    Autenticación personalizada que soporte tanto 'Token' como 'Bearer'
    para mayor flexibilidad con diferentes clientes HTTP.

    Ejemplos de headers soportados:
    - Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    - Authorization: Bearer 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
    """

    keyword = ["Token", "Bearer"]

    def authenticate(self, request):
        """
        Intenta autenticar con Token o Bearer
        """
        auth = self.get_authorization_header(request).split()

        if not auth or auth[0].lower() not in [
            k.lower().encode() for k in self.keyword
        ]:
            return None

        if len(auth) == 1:
            msg = "Invalid token header. No credentials provided."
            raise AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = "Invalid token header. Token string should not contain spaces."
            raise AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise AuthenticationFailed(msg)

        return self.authenticate_credentials(token)


class FlexibleTokenAuthentication(TokenAuthentication):
    """
    Autenticación más flexible que intenta múltiples formatos de token.

    Soporta:
    - Authorization: Token <token>
    - Authorization: Bearer <token>
    - Authorization: <token> (sin prefijo)
    """

    def get_authorization_header(self, request):
        """
        Override para manejar diferentes formatos de Authorization header
        """
        auth = request.META.get("HTTP_AUTHORIZATION", b"")
        if isinstance(auth, str):
            # Django 3.0+ puede devolver string en lugar de bytes
            auth = auth.encode("iso-8859-1")
        return auth

    def authenticate(self, request):
        """
        Intenta autenticar con diferentes formatos de token
        """
        auth_header = self.get_authorization_header(request)

        logger.debug(
            f"🔍 Auth header recibido: '{auth_header.decode('utf-8') if auth_header else 'None'}'"
        )

        if not auth_header:
            logger.debug("❌ No se encontró header Authorization")
            return None

        auth = auth_header.split()

        if not auth:
            logger.debug("❌ Header Authorization vacío después de split")
            return None

        # Caso 1: "Token <token>" o "Bearer <token>"
        if len(auth) == 2:
            auth_type = auth[0].decode("utf-8").lower()
            logger.debug(f"🔑 Tipo de auth detectado: '{auth_type}'")
            if auth_type in ["token", "bearer"]:
                try:
                    token = auth[1].decode("utf-8")
                    logger.debug(
                        f"✅ Token extraído (primeros 10 chars): '{token[:10]}...'"
                    )
                    result = self.authenticate_credentials(token)
                    if result:
                        logger.debug(
                            f"🎉 Autenticación exitosa para usuario: {result[0].username}"
                        )
                    else:
                        logger.debug("❌ authenticate_credentials devolvió None")
                    return result
                except UnicodeError:
                    logger.error("❌ Error de formato Unicode en token")
                    raise AuthenticationFailed("Invalid token format")

        # Caso 2: Solo el token sin prefijo
        elif len(auth) == 1:
            try:
                token = auth[0].decode("utf-8")
                logger.debug(f"🔍 Token sin prefijo detectado, longitud: {len(token)}")
                # Validar que parece un token válido (longitud mínima)
                if len(token) >= 20:  # Los tokens de Django suelen ser de 40 chars
                    logger.debug(
                        f"✅ Token válido sin prefijo (primeros 10 chars): '{token[:10]}...'"
                    )
                    result = self.authenticate_credentials(token)
                    if result:
                        logger.debug(
                            f"🎉 Autenticación exitosa (sin prefijo) para usuario: {result[0].username}"
                        )
                    return result
                else:
                    logger.debug(f"❌ Token muy corto: {len(token)} chars")
            except UnicodeError:
                logger.error("❌ Error de formato Unicode en token sin prefijo")
                pass

        # Si llegamos aquí, el formato no es reconocido
        logger.debug(f"❌ Formato de autenticación no reconocido. Parts: {len(auth)}")
        return None

    def authenticate_header(self, request):
        """
        Devuelve el string que debe usar el cliente para autenticarse
        """
        return "Token"  # Mantener compatibilidad con el estándar
