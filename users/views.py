from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from users.permissions import IsAdmin
from .models import User
from .serializers import CustomTokenSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .serializers import RegisterSerializer
from core.throttles import LoginThrottle
from rest_framework.permissions import AllowAny

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenSerializer
    throttle_classes = [LoginThrottle]