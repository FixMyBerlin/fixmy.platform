from django.contrib.gis.db.models.functions import AsGeoJSON
from django.http import JsonResponse
from .models import Project
import json

def edges(request):
    edges = Project.objects.all()
    result = []

    return JsonResponse(result, safe=False)

def projects(request):
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
