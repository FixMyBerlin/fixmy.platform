from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .notifications import send_double_opt_in
from .serializers import SignupSerializer, EventSignupSerializer


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()

            if request.data.get('newsletter', False):
                send_double_opt_in(instance)
            return Response(request.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventSignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = EventSignupSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()

            if request.data.get('newsletter', False):
                send_double_opt_in(request.data)
            return Response(request.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
