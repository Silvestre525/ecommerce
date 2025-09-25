#person/serializer.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Person
from django.db import transaction
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group

User = get_user_model()

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['name','last_name','dni','city']



class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    persona = PersonSerializer()

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ese usuario ya existe")
        return value
    
    @transaction.atomic
    def create(self, validated_data):
        # Datos de la persona
        person_data = validated_data.pop('persona')

        # Crear usuario
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Asignar al grupo visitante
        visitante_group, _ = Group.objects.get_or_create(name="Visitante")
        user.groups.add(visitante_group)

        # Crear la persona relacionada
        Person.objects.create(user=user, **person_data)

        # Crear token
        Token.objects.create(user=user)

        return user
