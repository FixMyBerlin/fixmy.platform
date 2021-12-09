import boto3
import sys

from datetime import datetime
from django.conf import settings
from django.db.models import Count
from django.http.response import Http404
from rest_framework import permissions, status, generics, filters
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import unquote

from fahrradparken.models import (
    ParkingFacility,
    Station,
    SurveyBicycleUsage,
    SurveyStation,
)

from .notifications import send_registration_confirmation
from .serializers import (
    EventSignupSerializer,
    ParkingFacilitySerializer,
    SignupSerializer,
    StaticStationSerializer,
    StationSerializer,
    SurveyBicycleUsageSerializer,
    SurveyStationSerializer,
    SurveyStationShortSerializer,
)


class CheckPreviousBicycleSurvey(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, session):
        """Check whether this session has created a bicycle usage survey."""
        does_exist = SurveyBicycleUsage.objects.filter(session=session).count() > 0
        return Response({"doesExist": does_exist}, status=200)


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


class SurveyInfoView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        survey_stations_count = SurveyStation.objects.count()
        survey_stations_session_count = (
            SurveyStation.objects.values('session').distinct().count()
        )
        survey_bicycle_usage_count = SurveyBicycleUsage.objects.count()
        stations_with_nps_count = (
            SurveyStation.objects.values('station')
            .annotate(count=Count('station'))
            .filter(count__gt=2)
            .count()
        )
        confirmed_parking_facilities_count = ParkingFacility.objects.filter(
            confirmations=2
        ).count()
        survey_stations_with_parking_facilities_count = (
            ParkingFacility.objects.distinct('station').count()
        )

        return Response(
            {
                "survey_stations_count": survey_stations_count,
                "survey_stations_session_count": survey_stations_session_count,
                "survey_stations_with_parking_facilities_count": survey_stations_with_parking_facilities_count,
                "survey_bicycle_usage_count": survey_bicycle_usage_count,
                "survey_stations_with_nps_count": stations_with_nps_count,
                "survey_confirmed_parking_facilities_count": confirmed_parking_facilities_count,
            }
        )


class StationList(generics.ListAPIView):
    queryset = Station.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'community']
    ordering = ['-travellers', 'community', '-is_long_distance', 'name']

    def list(self, request):
        """Searchable station listing as GeoJSON.

        Use the `search` URL parameter to filter by station name and community."""
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        is_static_only = self.request.query_params.get('full') is None
        if is_static_only:
            features = StaticStationSerializer(filtered_queryset, many=True)
        else:
            features = StationSerializer(filtered_queryset, many=True)
        return Response(data={'type': 'FeatureCollection', 'features': features.data})


class StationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get_object(self, pk):
        try:
            return Station.objects.prefetch_related('survey_responses').get(pk=pk)
        except Station.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        station = self.get_object(pk)
        serializer = StationSerializer(station, context={'request': request})
        return Response(serializer.data)


class SurveyStationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Add a new station survey response."""
        serializer = SurveyStationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(photo=request.data.get('photoS3'))
            count = SurveyStation.objects.filter(
                station=request.data['station']
            ).count()
            return Response({'count': count}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StationSurveysByUUID(generics.ListAPIView):
    serializer_class = SurveyStationShortSerializer

    def get_queryset(self):
        session = self.kwargs.get('session')
        return SurveyStation.objects.filter(session=session)


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


class PhotoUploadView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request, fname):
        """Upload a photo"""
        try:
            fname_decoded = unquote(fname)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        s3_client = boto3.client('s3')
        sort_path = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        s3_key = f"fahrradparken/user-uploads/{sort_path}/{fname_decoded}"

        try:
            s3_client.upload_fileobj(
                request.data['file'], settings.AWS_STORAGE_BUCKET_NAME, s3_key
            )
        except Exception as e:
            sys.stderr.write(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'path': s3_key})


class RawStationSurveyListing(generics.ListAPIView):
    queryset = SurveyStation.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering = ['station']

    def list(self, request):
        queryset = self.get_queryset()
        filtered_queryset = self.filter_queryset(queryset)
        serialized = SurveyStationSerializer(filtered_queryset, many=True)
        return Response(data=serialized.data)


class RawBicycleUsageSurveyListing(generics.ListAPIView):
    queryset = SurveyBicycleUsage.objects.all()

    def list(self, request):
        queryset = self.get_queryset()
        serialized = SurveyBicycleUsageSerializer(queryset, many=True)
        return Response(data=serialized.data)


class ParkingFacilityList(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = ParkingFacility.objects.all()
    serializer_class = ParkingFacilitySerializer


class ParkingFacilityDetail(RetrieveUpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = ParkingFacility.objects.all()
    serializer_class = ParkingFacilitySerializer
