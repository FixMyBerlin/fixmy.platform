from django.contrib.gis.db.models.functions import Transform
from django.contrib.gis.geos import GeometryCollection
from django.http import JsonResponse
from .models import Project
import json


def edges(request):
    edges = Project.objects.all()
    result = []

    return JsonResponse(result, safe=False)


def projects(request):
    result = {
        'type': 'FeatureCollection',
        'features': []
    }

    for p in Project.objects.all():
        feature = {
            'type': 'Feature',
            'geometry': json.loads(
                GeometryCollection(
                    [e.geom_4326 for e in p.edges.annotate(
                        geom_4326=Transform('geom', srid=4326)).all()]).json),
            'properties': {
                'name': p.name,
                'description': p.description
            }
        }
        result['features'].append(feature)

    return JsonResponse(result, safe=False)
