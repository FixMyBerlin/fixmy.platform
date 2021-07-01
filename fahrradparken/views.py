from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .notifications import send_registration_confirmation
from .serializers import SignupSerializer, EventSignupSerializer


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer_cls = (
            EventSignupSerializer
            if request.data.get('event_id') is not None
            else SignupSerializer
        )
        serializer = serializer_cls(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            send_registration_confirmation(instance)
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)