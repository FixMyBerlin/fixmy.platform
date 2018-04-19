from django.contrib.gis.db.models import Union
from django.http import JsonResponse
from .models import PlanningSection
import json


def edges(request):
    edges = PlanningSection.objects.all()
    result = []

    return JsonResponse(result, safe=False)


def projects(request):
    result = {
        'type': 'FeatureCollection',
        'features': []
    }

    for p in PlanningSection.objects.all():
        geometry = p.edges.aggregate(Union('geom'))['geom__union']
        feature = {
            'type': 'Feature',
            'geometry': json.loads(geometry.json),
            'properties': {
                'name': p.name,
                'description': p.description
            }
        }
        result['features'].append(feature)

    return JsonResponse(result)
