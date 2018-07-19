from django.contrib.gis.db.models import Union
from django.http import JsonResponse
from django.urls import reverse
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .models import Planning, PlanningSection, Profile
from .serializers import (
    PlanningSerializer, PlanningSectionSerializer, ProfileSerializer
)
import json


class PlanningList(generics.ListAPIView):
    queryset = Planning.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSerializer


class PlanningDetail(generics.RetrieveAPIView):
    queryset = Planning.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSerializer


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

    if request.GET.get('has-planning', 0):
        qs = PlanningSection.objects.filter(plannings__isnull=False)
    else:
        qs = PlanningSection.objects.all()

    for p in qs:
        geometry = p.edges.aggregate(Union('geom'))['geom__union'].merged
        feature = {
            'type': 'Feature',
            'geometry': json.loads(geometry.json),
            'properties': {
                'id': p.pk,
                'name': p.name,
                'velocity': (p.velocity_index(0) + p.velocity_index(1)) / 2,
                'safety': (p.safety_index(0) + p.safety_index(1)) / 2,
                'side0_velocity': p.velocity_index(0),
                'side0_safety': p.safety_index(0),
                'side1_velocity': p.velocity_index(1),
                'side1_safety': p.safety_index(1)
            }
        }

        for planning in p.plannings.all():
            prefix = 'side{}_'.format(planning.side)
            planning_url = request.build_absolute_uri(
                reverse('planning-detail', args=[planning.id])
            )
            feature['properties'][prefix + 'planning_url'] = planning_url
            feature['properties'][prefix + 'planning_title'] = planning.title
            feature['properties'][prefix + 'planning_phase'] = planning.phase

        for detail in p.details.all():
            prefix = 'side{}_'.format(detail.side)
            feature['properties'][prefix + 'orientation'] = detail.orientation

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
