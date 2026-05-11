from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import PersonSerializer

class AuthService:
    """
    Servicio para el manejo de la autenticación
    """
    
    @staticmethod
    def authenticate_user(username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValueError("Invalid username or password.")
        if not user.is_active:
            raise PermissionError("User account is disabled.")
            
        token, created = Token.objects.get_or_create(user=user)
        return user, token
        
    @staticmethod
    def register_user(serializer):
        user = serializer.save()
        token = Token.objects.get(user=user)
        return user, token

class PersonService:
    """
    Servicio para el manejo del perfil
    """
    
    @staticmethod
    def get_profile_data(user):
        try:
            persona = user.person
            persona_data = PersonSerializer(persona).data
        except Exception:
            persona_data = None
            
        return {
            "username": user.username,
            "email": user.email,
            "persona": persona_data,
            "groups": list(user.groups.values_list("name", flat=True)),
        }
