import io

from django.contrib.gis.db.models import Union
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from fixmyapp.importing import import_planning_sections
from fixmyapp.serializers import FileSerializer
from .models import PlanningSection
import json
import random


@api_view()
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
                'side0_progress': p.progress,
                'side0_index': round(random.randint(5,50)*0.1, 1),
                'side1_progress': p.progress,
                'side1_index': round(random.randint(5,50)*0.1, 1)
            }
        }
        result['features'].append(feature)

    return Response(result)


@api_view()
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

    return Response(result)


class UploadEdges(CreateAPIView):
    """
    Lets you upload a new .shp file with edges, overriding any existing ones.

    TODO: Extract importing logic from management command and call here.
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        bytes_file = request.data['file']
        text_file = io.StringIO(bytes_file.read().decode('utf-8'))
        # TODO import_edges(file_like)
        return Response("Success", status=status.HTTP_201_CREATED)


class UploadPlanningSections(CreateAPIView):
    """
    Lets you upload a new .csv file with new planning sections, overriding any existing ones.

    TODO: This works, but is slow and might trigger a time-out.
    """
    parser_classes = (MultiPartParser, FormParser,)
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        bytes_file = request.data['file']
        text_file = io.StringIO(bytes_file.read().decode('utf-8'))
        import_planning_sections(text_file)
        return Response("Success", status=status.HTTP_201_CREATED)
