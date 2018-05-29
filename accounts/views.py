from rest_framework.generics import CreateAPIView
from .serializers import UserSerializer


class UserCreate(CreateAPIView):
    """
    Lets you create a new user
    """
    serializer_class = UserSerializer
