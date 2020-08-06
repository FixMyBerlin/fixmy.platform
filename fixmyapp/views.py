import dateutil.parser
import boto3
import uuid
from datetime import datetime, timezone
from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Like,
    GastroSignup,
    Profile,
    Project,
    Report,
    Section,
    PlaystreetSignup,
)
from .serializers import (
    FeedbackSerializer,
    GastroSignupSerializer,
    GastroDirectRegistrationSerializer,
    GastroRegistrationSerializer,
    GastroCertificateSerializer,
    PlaystreetSignupSerializer,
    ProfileSerializer,
    ProjectSerializer,
    ReportSerializer,
    SectionSerializer,
)
from .signals import sign_up_newsletter
import requests


class DefaultPagination(PageNumberPagination):
    max_page_size = 1000
    page_size = 10
    page_size_query_param = 'page_size'


class LikedByUserProjectList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(
            likes__in=Like.objects.filter(user=self.request.user)
        ).order_by('id')


class LikedByUserReportList(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = DefaultPagination
    serializer_class = ReportSerializer

    def get_queryset(self):
        return Report.objects.filter(
            likes__in=Like.objects.filter(user=self.request.user)
        ).order_by('id')


class ProjectList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = (
        Project.objects.filter(published=1).order_by('id').prefetch_related('likes')
    )
    serializer_class = ProjectSerializer


class ProjectDetail(generics.RetrieveAPIView):
    queryset = Project.objects.filter(published=1)
    serializer_class = ProjectSerializer


class SectionList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = Section.objects.all().order_by('id')
    serializer_class = SectionSerializer


class SectionDetail(generics.RetrieveAPIView):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer


class ReportList(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Report.objects.filter(published=1).prefetch_related(
        'likes', 'bikestands'
    )
    serializer_class = ReportSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class ReportDetail(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.AllowAny,)
    queryset = Report.objects.filter(published=1)
    serializer_class = ReportSerializer

    def perform_update(self, serializer):
        """Allows associating a user with a report instance once.

        Once a user is associated with a report, no further updates are allowed
        via the API.
        """
        if self.get_object().user:
            raise PermissionDenied
        else:
            super(ReportDetail, self).perform_update(serializer)


class LikeView(APIView):
    """Base class for liking resources
    """

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, model, format=None):
        """Returns the number of likes for an object
        """

        instance = get_object_or_404(model, pk=pk)
        if request.user.is_authenticated:
            likes_by_user = instance.likes.filter(user=request.user).count()
        else:
            likes_by_user = 0
        likes = instance.likes.count()
        result = {'user_has_liked': bool(likes_by_user), 'likes': likes}
        return Response(result)

    def post(self, request, pk, model, format=None):
        """Adds or removes a like by the current authenticated user
        """
        instance = get_object_or_404(model, pk=pk)
        if instance.likes.filter(user=request.user).count() == 0:
            Like.objects.create(content_object=instance, user=request.user)
            user_has_liked = True
            response_status = status.HTTP_201_CREATED
        else:
            instance.likes.filter(user=request.user).delete()
            user_has_liked = False
            response_status = status.HTTP_200_OK

        result = {'user_has_liked': user_has_liked, 'likes': instance.likes.count()}
        return Response(result, status=response_status)


class PlayStreetView(APIView):
    permission_classes = (permissions.AllowAny,)

    def make_listing(self, campaign):
        results = (
            PlaystreetSignup.objects.filter(campaign=campaign)
            .values('street')
            .annotate(signups=Count('street'))
        )
        return {res['street']: res['signups'] for res in results}

    def get(self, request, campaign):
        """Returns a listing overview of cumulative signups per street."""
        return Response(self.make_listing(campaign))

    def put(self, request, campaign):
        """Adds new signups."""
        serializer = PlaystreetSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(self.make_listing(campaign), status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GastroSignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def _send_registration_confirmation(self, recipient, request):
        """Send a registration confirmation email notice"""
        subject = 'Ihr Antrag bei XHain-Terrassen'
        body = render_to_string('gastro/notice_registered.txt', request=request)
        mail.send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True
        )

    def get(self, request, campaign, pk, access_key=None):
        """Request existing signup data"""
        result = get_object_or_404(GastroSignup, pk=pk)

        serialization = GastroRegistrationSerializer(result).data
        return Response(serialization)

    def post(self, request, campaign):
        """Adds new signups."""

        def gastro_signups_open():
            try:
                start = dateutil.parser.parse(settings.GASTRO_SIGNUPS_OPEN)
                end = dateutil.parser.parse(settings.GASTRO_SIGNUPS_CLOSE)
            except TypeError:
                # No explicit start and end times defined
                return True
            rv = start < datetime.now(tz=timezone.utc) < end
            return rv

        if not settings.TOGGLE_GASTRO_SIGNUPS or not gastro_signups_open():
            return Response(
                'Signups are currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        if settings.TOGGLE_GASTRO_DIRECT_SIGNUP:
            serializer = GastroDirectRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                instance = serializer.save(
                    status=GastroSignup.STATUS_REGISTERED,
                    certificate=request.data.get('certificateS3'),
                    application_received=datetime.now(tz=timezone.utc),
                )
                self._send_registration_confirmation(instance.email, request)
                return Response(request.data, status=status.HTTP_201_CREATED)
        else:
            serializer = GastroSignupSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(request.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, campaign, pk, access_key):
        """Adds registration data to an existing signup."""
        if not settings.TOGGLE_GASTRO_REGISTRATIONS:
            return Response(
                'Registration is currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        instance = get_object_or_404(GastroSignup, pk=pk, access_key=access_key)

        if instance.status not in [
            GastroSignup.STATUS_REGISTRATION,
            GastroSignup.STATUS_REGISTERED,
        ]:
            return Response(
                'This application is locked', status=status.HTTP_405_METHOD_NOT_ALLOWED
            )

        serializer = GastroRegistrationSerializer(instance=instance, data=request.data)
        if serializer.is_valid():
            serializer.save(
                status=GastroSignup.STATUS_REGISTERED,
                application_received=datetime.now(tz=timezone.utc),
            )

            self._send_registration_confirmation(instance.email, request)
            return Response(request.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GastroCertificateView(APIView):
    permission_classes = (permissions.AllowAny,)
    parser_classes = [FileUploadParser]
    serializer_class = GastroCertificateSerializer

    def post(self, request, campaign, fname):
        """Upload a certificate without existing signup"""
        if not settings.TOGGLE_GASTRO_REGISTRATIONS:
            return Response(
                'Registration is currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        s3_client = boto3.client('s3')
        sort_path = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        s3_key = f"{campaign}/gastro/{sort_path}/{fname}"

        try:
            s3_client.upload_fileobj(
                request.data['file'], settings.AWS_STORAGE_BUCKET_NAME, s3_key
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response({'path': s3_key})

    def put(self, request, campaign, pk, access_key):
        """Upload a certificate for an existing signup"""
        if not settings.TOGGLE_GASTRO_REGISTRATIONS:
            return Response(
                'Registration is currently not open',
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        instance = get_object_or_404(
            GastroSignup, campaign=campaign, pk=pk, access_key=access_key
        )

        try:
            instance.certificate = request.data['file']
            instance.save()
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class GastroRenewalView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, campaign, pk, access_key):
        """Request information about the possibility to renew an application"""

        result = get_object_or_404(GastroSignup, pk=pk)

        print(type(result.access_key_renewal), type(access_key))

        if result.access_key_renewal != uuid.UUID(access_key):
            return Response(
                _('Invalid access key'), status=status.HTTP_401_UNAUTHORIZED
            )

        serialization = GastroRegistrationSerializer(result).data
        return Response(serialization)

    def post(self, request, campaign, pk, access_key):
        """Submit a renewal application"""
        application = get_object_or_404(GastroSignup, pk=pk)

        renewal_campaign = GastroSignup.RENEWAL_CAMPAIGN.get(application.campaign, None)

        if renewal_campaign is None:
            return Response(
                _('No renewal defined for this campaign'),
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        try:
            if application.access_key_renewal != uuid.UUID(access_key):
                return Response(
                    _('Invalid access key'), status=status.HTTP_401_UNAUTHORIZED
                )
        except ValueError:
            return Response(
                _('Invalid access key'), status=status.HTTP_401_UNAUTHORIZED
            )

        if (
            datetime.now(tz=timezone.utc).date()
            >= GastroSignup.CAMPAIGN_DURATION[renewal_campaign][1]
        ):
            return Response(_('Campaign has ended'), status=status.HTTP_400_BAD_REQUEST)

        # Create a new instance by setting primary key to `None`
        renewal = application
        renewal.pk = None

        renewal.campaign = renewal_campaign
        renewal.received = datetime.now(tz=timezone.utc)
        renewal.status = GastroSignup.STATUS_ACCEPTED
        renewal.application_decided = datetime.now(tz=timezone.utc)
        renewal.set_application_decided()
        renewal.access_key = uuid.uuid4()
        renewal.access_key_renewal = uuid.uuid4()
        renewal.renewal_sent_on = None
        renewal.save()

        prev_application = GastroSignup.objects.get(pk=pk)
        prev_application.renewal_application = renewal
        prev_application.save()

        renewal.send_notice()
        renewal.save()

        serialization = GastroRegistrationSerializer(prev_application).data
        return Response(serialization)


@api_view(['PUT'])
def profile(request, profile_id):
    try:
        obj = Profile.objects.get(pk=profile_id)
        serializer = ProfileSerializer(obj, data=request.data)
        success_status = status.HTTP_200_OK
    except Profile.DoesNotExist:
        serializer = ProfileSerializer(data=request.data)
        success_status = status.HTTP_201_CREATED
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=success_status)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def feedback(request):
    serializer = FeedbackSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        subject = 'Feedback received'.format(serializer.data['email'])
        message = 'From: {} <{}>\nSubject: {}\n\n{}'.format(
            serializer.data['name'],
            serializer.data['email'],
            serializer.data['subject'],
            serializer.data['message'],
        )
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def newsletter_signup(request):
    if not settings.TOGGLE_NEWSLETTER:
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
    try:
        sign_up_newsletter(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    except requests.exceptions.RequestException:
        return Response(status=status.HTTP_502_BAD_GATEWAY)
