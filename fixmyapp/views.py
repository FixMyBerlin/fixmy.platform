from django.contrib.gis.db.models.functions import AsGeoJSON
from django.http import JsonResponse
from django.core.serializers import serialize
from .models import Kanten, Project
import json


def api(request):
    projects = Project.objects.all()
    result = []

    for p in projects:
        features = {
            'type': 'FeatureCollection',
            'features': [json.loads(e.json) for e in p.edges.annotate(json=AsGeoJSON('geom')).all()],
            'properties': {
                'name': p.name,
                'description': p.description
            }
        }
        result.append(features)

    return JsonResponse(result, safe=False)
