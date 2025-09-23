from django.shortcuts import render
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, PersonSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

# Create your views here.



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = Token.object.get(user=user)

            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        persona = getattr(request.user, 'persona', None)
        return Response({
            'username': request.user.username,
            'email': request.user.email,
            'persona': PersonSerializer(persona).data if persona else None,
            'groups': list(request.user.groups.values_list('name', flat=True))
        })