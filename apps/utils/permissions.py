# utils/permissions.py
from rest_framework.permissions import BasePermission

class IsAdministrador(BasePermission):
    """
    Permite acceso solo a usuarios del grupo 'Administrador'.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Administrador').exists()

class IsVisitante(BasePermission):
    """
    Permite acceso solo a usuarios del grupo 'Visitante'.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Visitante').exists()
