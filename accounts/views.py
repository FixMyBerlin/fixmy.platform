from .serializers import UserSerializer
from rest_framework import generics


class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer
