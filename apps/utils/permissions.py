# utils/permissions.py
import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsAdministrador(BasePermission):
    """
    Permite acceso solo a usuarios del grupo 'Administrador'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.debug(f"IsAdministrador: Usuario no autenticado")
            return False

        is_admin = request.user.groups.filter(name="Administrador").exists()
        logger.debug(
            f"IsAdministrador: Usuario {request.user.username}, es_admin: {is_admin}"
        )
        return is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsVisitante(BasePermission):
    """
    Permite acceso solo a usuarios del grupo 'Visitante'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.debug(f"IsVisitante: Usuario no autenticado")
            return False

        is_visitante = request.user.groups.filter(name="Visitante").exists()
        logger.debug(
            f"IsVisitante: Usuario {request.user.username}, es_visitante: {is_visitante}"
        )
        return is_visitante

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdministradorOrVisitante(BasePermission):
    """
    Permite acceso a usuarios de los grupos 'Administrador' o 'Visitante'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.debug(f"IsAdministradorOrVisitante: Usuario no autenticado")
            return False

        user_groups = request.user.groups.values_list("name", flat=True)
        has_access = any(
            group in ["Administrador", "Visitante"] for group in user_groups
        )
        logger.debug(
            f"IsAdministradorOrVisitante: Usuario {request.user.username}, grupos: {list(user_groups)}, acceso: {has_access}"
        )
        return has_access

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdministradorOrReadOnly(BasePermission):
    """
    Permite escritura solo a Administradores, pero lectura a cualquier usuario autenticado.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # Permisos de lectura para cualquier usuario autenticado
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            logger.debug(
                f"IsAdministradorOrReadOnly: Permiso de lectura para {request.user.username}"
            )
            return True

        # Permisos de escritura solo para administradores
        is_admin = request.user.groups.filter(name="Administrador").exists()
        logger.debug(
            f"IsAdministradorOrReadOnly: Permiso de escritura para {request.user.username}, es_admin: {is_admin}"
        )
        return is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwnerOrAdministrador(BasePermission):
    """
    Permite acceso al propietario del objeto o a un Administrador.
    Útil para perfiles de usuario, pedidos, etc.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Administradores tienen acceso total
        if request.user.groups.filter(name="Administrador").exists():
            logger.debug(
                f"IsOwnerOrAdministrador: Acceso de administrador para {request.user.username}"
            )
            return True

        # Verificar si es el propietario según el tipo de objeto
        is_owner = False

        # Para órdenes (Order model)
        if hasattr(obj, "person") and hasattr(obj.person, "user"):
            is_owner = obj.person.user == request.user
            logger.debug(
                f"IsOwnerOrAdministrador: Verificando orden - Usuario {request.user.username}, propietario: {obj.person.user.username if obj.person.user else 'None'}, es_propietario: {is_owner}"
            )
        # Para perfiles de persona (Person model)
        elif hasattr(obj, "user"):
            is_owner = obj.user == request.user
            logger.debug(
                f"IsOwnerOrAdministrador: Verificando perfil - Usuario {request.user.username}, es_propietario: {is_owner}"
            )
        # Para objetos con método get_owner()
        elif hasattr(obj, "get_owner"):
            is_owner = obj.get_owner() == request.user
            logger.debug(
                f"IsOwnerOrAdministrador: Verificando con get_owner() - Usuario {request.user.username}, es_propietario: {is_owner}"
            )
        else:
            logger.debug(
                f"IsOwnerOrAdministrador: No se pudo determinar propietario para {type(obj).__name__}"
            )

        return is_owner
