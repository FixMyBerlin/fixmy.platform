from django.conf import settings
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Like,
    Profile,
    Project,
    Report,
    Section
)
from .serializers import (
    FeedbackSerializer,
    ProfileSerializer,
    ProjectSerializer,
    ReportSerializer,
    SectionSerializer
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
    queryset = (Project.objects
        .filter(published=1)
        .order_by('id')
        .prefetch_related('likes')
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
    queryset = Report.objects.filter(published=1).prefetch_related('likes', 'bikestands')
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
        result = {
            'user_has_liked': bool(likes_by_user),
            'likes': likes
        }
        return Response(result)

    def post(self, request, pk, model, format=None):
        """Adds or removes a like by the current authenticated user
        """
        instance = get_object_or_404(model, pk=pk)
        if instance.likes.filter(user=request.user).count() == 0:
            Like.objects.create(
                content_object=instance,
                user=request.user
            )
            user_has_liked = True
            response_status = status.HTTP_201_CREATED
        else:
            instance.likes.filter(user=request.user).delete()
            user_has_liked = False
            response_status = status.HTTP_200_OK

        result = {
            'user_has_liked': user_has_liked,
            'likes': instance.likes.count()
        }
        return Response(result, status=response_status)


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
            serializer.data['message']
        )
        mail.send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL]
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
