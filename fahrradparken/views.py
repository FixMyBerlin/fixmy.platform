import json

from rest_framework import permissions, status, generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from fahrradparken.models import Station, SurveyStation

from .notifications import send_registration_confirmation
from .serializers import (
    SignupSerializer,
    EventSignupSerializer,
    StationSerializer,
    SurveyBicycleUsageSerializer,
    SurveyStationSerializer,
    SurveyStationShortSerializer,
)


class SignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Create a new signup entry, sending out a confirmation email on success.

        An event signup is created if an `event_id` is passed in the request
        body and a regular signup otherwise."""
        try:
            serializer_cls = (
                EventSignupSerializer
                if request.data.get('event_id') is not None
                else SignupSerializer
            )
        except AttributeError:
            # The above will throw when trying to access `data` on an empty
            # request.
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
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'community']

    def get(self, request):
        """Searchable station listing as GeoJSON.

        Use the `search` URL parameter to filter by station name and community."""
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)

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
        for station in filtered_queryset.all():
            props = dict([(field, getattr(station, field)) for field in INCLUDE_FIELDS])
            features.append(
                {
                    'type': 'Feature',
                    # convert the location geometry to a data type that is
                    # json-compatible
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


class StationSurveysByUUID(generics.ListAPIView):
    queryset = SurveyStation.objects.all()
    serializer_class = SurveyStationShortSerializer


class SurveyBicycleUsageView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Add a new bicycle usage survey response."""
        serializer = SurveyBicycleUsageSerializer(data=request.data)
        if serializer.is_valid():
            linked_surveys = SurveyStation.objects.filter(
                session=request.data.get('session')
            )
            if linked_surveys.count() == 0:
                return Response(
                    'Bicycle usage survey requires at least one station survey',
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()
            return Response(
                request.data,
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
