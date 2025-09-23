#person/serializer.py
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Person
from django.db import transaction
from rest_framework.authtoken.models import Token

User = get_user_model

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
        person_data = validated_data.pop('persona')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Person.objects.create(user=user, **person_data)
        Token.objects.create(user=user) # crear token (se puede obtener luego con obtain_auth_token también)
        return user