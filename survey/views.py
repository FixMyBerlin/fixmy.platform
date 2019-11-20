from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Rating, Scene, Survey
from .serializers import RatingSerializer, SurveySerializer


class SurveyView(APIView):

    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def put(self, request, project, session):
        serializer = SurveySerializer(data={
            'session_id': session,
            'profile': request.data,
            'project': project
        })

        if serializer.is_valid(raise_exception=True):
            survey = serializer.save()
            perspective = survey.profile.get('perspective')
            size = 10 if perspective == Scene.PERSPECTIVE_C else 5
            scenes = Scene.random_group(perspective, project, size)
            total_ratings = Rating.objects.filter(rating__isnull=False).count()

            for s in scenes:
                Rating.objects.create(scene=s, survey=survey)

            return Response(
                data={
                    'scenes': [str(s) for s in scenes],
                    'ratings_total': total_ratings
                },
                status=status.HTTP_201_CREATED
            )

    @transaction.atomic
    def post(self, request, project, session):
        perspective = request.data.get('perspective')
        size = 10 if perspective == Scene.PERSPECTIVE_C else 5

        scenes = Scene.random_group(perspective, project, size)
        total_ratings = Rating.objects.filter(rating__isnull=False).count()
        survey = Survey.objects.get(id=session)

        for s in scenes:
            Rating.objects.create(scene=s, survey=survey)

        return Response(
            data={
                'scenes': [str(s) for s in scenes],
                'ratings_total': total_ratings
            },
            status=status.HTTP_200_OK
        )


@api_view(['PUT'])
@permission_classes((permissions.AllowAny,))
def add_rating(request, project, session, scene_id):
    scene = Scene.find_by_scene_id(scene_id)
    rating = get_object_or_404(Rating, survey=session, scene=scene)
    serializer = RatingSerializer(rating, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
