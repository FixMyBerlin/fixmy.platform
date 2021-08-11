import json

from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from fahrradparken.models import Station

from .notifications import send_registration_confirmation
from .serializers import (
    SignupSerializer,
    EventSignupSerializer,
    StationSerializer,
    SurveyBicycleUsageSerializer,
    SurveyStationSerializer,
)


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        try:
            serializer_cls = (
                EventSignupSerializer
                if request.data.get('event_id') is not None
                else SignupSerializer
            )
        except AttributeError:
            return Response('Missing request body', status=status.HTTP_400_BAD_REQUEST)

        serializer = serializer_cls(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            send_registration_confirmation(instance)
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationList(generics.ListAPIView):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get(self, request):
        INCLUDE_FIELDS = (
            'id',
            'name',
            'travellers',
            'post_code',
            'is_long_distance',
            'is_light_rail',
            'community',
        )
        features = []
        for station in Station.objects.all():
            props = dict([(field, getattr(station, field)) for field in INCLUDE_FIELDS])
            features.append(
                {
                    'type': 'Feature',
                    'geometry': json.loads(station.location.json),
                    'properties': props,
                }
            )
        return Response(data={'type': 'FeatureCollection', 'features': features})


class SurveyStationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Add a new station survey response."""
        serializer = SurveyStationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SurveyBicycleUsageView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Add a new bicycle usage survey response."""
        serializer = SurveyBicycleUsageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                request.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
