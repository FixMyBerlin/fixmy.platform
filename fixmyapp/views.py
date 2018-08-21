from django.conf import settings
from django.core import mail
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Planning, PlanningSection, Profile
from .serializers import (
    FeedbackSerializer,
    PlanningSerializer,
    PlanningSectionSerializer,
    ProfileSerializer
)


class DefaultPagination(PageNumberPagination):
    max_page_size = 100
    page_size = 10
    page_size_query_param = 'page_size'


class PlanningList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer


class PlanningDetail(generics.RetrieveAPIView):
    queryset = Planning.objects.all()
    serializer_class = PlanningSerializer


class PlanningSectionList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = PlanningSection.objects.all()
    serializer_class = PlanningSectionSerializer


class PlanningSectionDetail(generics.RetrieveAPIView):
    queryset = PlanningSection.objects.all()
    serializer_class = PlanningSectionSerializer


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
