from django.conf import settings
from django.core import mail
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Like, Planning, PlanningSection, Profile
from .serializers import (
    FeedbackSerializer,
    PlanningSerializer,
    PlanningSectionSerializer,
    ProfileSerializer
)


class DefaultPagination(PageNumberPagination):
    max_page_size = 1000
    page_size = 10
    page_size_query_param = 'page_size'


class PlanningList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = Planning.objects.filter(published=1).prefetch_related(
        'planning_sections', 'planning_sections__details')
    serializer_class = PlanningSerializer


class PlanningDetail(generics.RetrieveAPIView):
    queryset = Planning.objects.filter(published=1)
    serializer_class = PlanningSerializer


class PlanningSectionList(generics.ListAPIView):
    pagination_class = DefaultPagination
    queryset = PlanningSection.objects.all().prefetch_related(
        'details', 'planning_set')
    serializer_class = PlanningSectionSerializer


class PlanningSectionDetail(generics.RetrieveAPIView):
    queryset = PlanningSection.objects.all()
    serializer_class = PlanningSectionSerializer


class LikeView(APIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get(self, request, pk, format=None):
        """Returns the number of likes for the planning
        """
        planning = get_object_or_404(Planning, pk=pk)
        if request.user.is_authenticated:
            likes_by_user = planning.likes.filter(user=request.user).count()
        else:
            likes_by_user = 0
        likes = planning.likes.count()
        result = {
            'user_has_liked': bool(likes_by_user),
            'likes': likes
        }
        return Response(result)

    def post(self, request, pk, format=None):
        """Adds or removes a like by the current authenticated user
        """
        planning = get_object_or_404(Planning, pk=pk)
        if planning.likes.filter(user=request.user).count() == 0:
            Like.objects.create(
                content_object=planning,
                user=request.user
            )
            user_has_liked = True
            response_status = status.HTTP_201_CREATED
        else:
            planning.likes.filter(user=request.user).delete()
            user_has_liked = False
            response_status = status.HTTP_200_OK

        result = {
            'user_has_liked': user_has_liked,
            'likes': planning.likes.count()
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
