from django.db import transaction
from django.db.models import Prefetch
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Rating, Scene, Session
from .serializers import RatingSerializer, SessionSerializer


class SurveyView(APIView):

    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def put(self, request, project, session):
        serializer = SessionSerializer(
            data={'session_id': session, 'profile': request.data, 'project': project}
        )

        if serializer.is_valid(raise_exception=True):
            session = serializer.save()
            perspective = session.profile.get('perspective')
            size = 10 if perspective == Scene.PERSPECTIVE_C else 5
            scenes = Scene.random_group(perspective, project, size)
            total_ratings = Rating.objects.filter(rating__isnull=False).count()

            for s in scenes:
                Rating.objects.create(scene=s, session=session)

            return Response(
                data={
                    'scenes': [str(s) for s in scenes],
                    'ratings_total': total_ratings,
                },
                status=status.HTTP_201_CREATED,
            )

    @transaction.atomic
    def post(self, request, project, session):
        perspective = request.data.get('perspective')
        size = 10 if perspective == Scene.PERSPECTIVE_C else 5

        scenes = Scene.random_group(perspective, project, size)
        total_ratings = Rating.objects.filter(rating__isnull=False).count()
        session = Session.objects.get(id=session)

        for s in scenes:
            Rating.objects.create(scene=s, session=session)

        return Response(
            data={'scenes': [str(s) for s in scenes], 'ratings_total': total_ratings},
            status=status.HTTP_200_OK,
        )


@api_view(['PUT'])
@permission_classes((permissions.AllowAny,))
def add_rating(request, project, session, scene_id):
    scene = Scene.find_by_scene_id(scene_id)
    rating = Rating.objects.filter(session=session, scene=scene).order_by('id').last()
    if rating is None:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = RatingSerializer(rating, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def results(request, project):
    prefetch_ratings = Prefetch('ratings', queryset=Rating.objects.order_by('id'))
    queryset = Session.objects.filter(project=project).prefetch_related(
        prefetch_ratings
    )
    data = SessionSerializer(queryset, many=True).data

    return Response(data, status=status.HTTP_200_OK)
