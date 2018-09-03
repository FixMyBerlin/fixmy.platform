from .serializers import UserSerializer
from rest_framework import generics
from rest_framework import permissions


class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)
