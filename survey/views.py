from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Scene, Rating
from .serializers import SurveySerializer


class SurveyView(APIView):

    permission_classes = (permissions.AllowAny,)
    perspective_map = {
        'bicycle': ('C', 10),
        'car': ('A', 5),
        'pedestrian': ('P', 5),
    }

    @transaction.atomic
    def put(self, request, project, session):
        serializer = SurveySerializer(data={
            'id': session,
            'profile': request.data,
            'project': project
        })

        if serializer.is_valid():
            survey = serializer.save()
            perspective_ = survey.profile.get('perspective')
            perspective = self.perspective_map[perspective_][0]
            size = self.perspective_map[perspective_][1]
            scenes = Scene.random_group(perspective, project, size)
            total_ratings = Rating.objects.count()

            for s in scenes:
                Rating.objects.create(scene=s, survey=survey)

            return Response(
                data={
                    'scenes': [str(s) for s in scenes],
                    'ratings_total': total_ratings
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def post(self, request, project, session):
        pass


@api_view(['PUT'])
@permission_classes((permissions.AllowAny,))
def add_rating(request, project, session, scene_id):
    scene = Scene.find_by_scene_id(scene_id)
    rating = get_object_or_404(Rating, survey=session, scene=scene)
    rating.duration = request.data.get('duration')
    rating.rating = request.data.get('rating')
    rating.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
