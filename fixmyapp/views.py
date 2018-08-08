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
import copy
import json


class PlanningList(generics.ListAPIView):
    queryset = Planning.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSerializer


class PlanningDetail(generics.RetrieveAPIView):
    queryset = Planning.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSerializer


class PlanningSectionDetail(generics.RetrieveAPIView):
    queryset = PlanningSection.objects.all()
    renderer_classes = (JSONRenderer,)
    serializer_class = PlanningSectionSerializer


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
                'velocity': p.velocity_index(),
                'safety': p.safety_index()
            }
        }

        for detail in p.details.all():
            prefix = 'side{}_'.format(detail.side)
            feature['properties'][prefix + 'orientation'] = detail.orientation
            feature['properties'][prefix + 'velocity'] = detail.velocity_index()
            feature['properties'][prefix + 'safety'] = detail.safety_index()

        if p.has_plannings():
            feature['properties'].update(
                properties_from_plannings(list(p.plannings.all()), request))

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


def properties_from_plannings(plannings, request):
    properties = {}

    if len(plannings) == 1 and plannings[0].side == Planning.BOTH:
        plannings.append(copy.copy(plannings[0]))
        plannings[0].side = Planning.RIGHT
        plannings[1].side = Planning.LEFT

    for planning in plannings:
        prefix = 'side{}_'.format(planning.side)
        planning_url = request.build_absolute_uri(
            reverse('planning-detail', args=[planning.id])
        )
        properties[prefix + 'planning_url'] = planning_url
        properties[prefix + 'planning_title'] = planning.title
        properties[prefix + 'planning_phase'] = planning.phase

    if len(plannings) == 2:
        if plannings[0].phase is not None and plannings[1].phase is not None:
            properties['planning_phase'] = Planning.PHASE_CHOICES[max(
                Planning.PHASE_CHOICES.index(
                    (plannings[0].phase, plannings[0].phase)),
                Planning.PHASE_CHOICES.index(
                    (plannings[1].phase, plannings[1].phase))
            )][1]
        elif plannings[0].phase is not None:
            properties['planning_phase'] = plannings[0].phase
        else:
            properties['planning_phase'] = plannings[1].phase
    else:
        properties['planning_phase'] = plannings[0].phase

    return properties
