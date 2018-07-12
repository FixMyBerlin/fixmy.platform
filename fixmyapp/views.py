from django.contrib.gis.db.models import Union
from django.http import JsonResponse
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .models import Planning, PlanningSection, Profile
from .serializers import (
    PlanningSerializer, PlanningSectionSerializer, ProfileSerializer
)
import json


class PlanningDetail(generics.GenericAPIView, mixins.RetrieveModelMixin):
    queryset = Planning.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class PlanningSectionDetail(generics.GenericAPIView, mixins.RetrieveModelMixin):
    queryset = PlanningSection.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSectionSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


def planning_sections(request):
    result = {
        'type': 'FeatureCollection',
        'features': []
    }

    for p in PlanningSection.objects.all():
        geometry = p.edges.aggregate(Union('geom'))['geom__union'].merged
        feature = {
            'type': 'Feature',
            'geometry': json.loads(geometry.json),
            'properties': {
                'id': p.pk,
                'name': p.name,
                'v': (p.velocity_index(0) + p.velocity_index(1)) / 2,
                's': (p.safety_index(0) + p.safety_index(1)) / 2,
                'side0_progress': p.progress,
                'side0_v': p.velocity_index(0),
                'side0_s': p.safety_index(0),
                'side1_progress': p.progress,
                'side1_v': p.velocity_index(1),
                'side1_s': p.safety_index(1)
            }
        }
        result['features'].append(feature)

    return JsonResponse(result)


def planning_sections_in_progress(request):
    result = {
        'type': 'FeatureCollection',
        'features': []
    }

    for p in PlanningSection.objects.filter(progress__gt=0):
        geometry = p.edges.aggregate(Union('geom'))['geom__union'].merged
        feature = {
            'type': 'Feature',
            'geometry': json.loads(geometry.json),
            'properties': {
                'id': p.pk,
                'name': p.name,
                'progress': p.progress,
                'side': 0
            }
        }
        result['features'].append(feature)
        center = {
            'type': 'Feature',
            'geometry': json.loads(geometry.point_on_surface.json),
            'properties': {
                'id': p.pk
            }
        }
        result['features'].append(center)

    return JsonResponse(result)


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
