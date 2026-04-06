from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone
from rest_framework.serializers import ValidationError

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'role', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'viewer')
        )


class CustomTokenSerializer(TokenObtainPairSerializer):
    username_field = "email" 
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_active:
            raise ValidationError("User account is disabled")

        User.objects.filter(id=self.user.id).update(last_login=timezone.now())
        data["role"] = self.user.role

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token