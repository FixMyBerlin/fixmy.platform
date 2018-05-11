from django.contrib.gis.db.models import Union
from django.http import JsonResponse
from .models import PlanningSection
import json


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
                'progress': p.progress,
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
            'geometry': json.loads(geometry.centroid.json),
            'properties': {
                'id': p.pk
            }
        }
        result['features'].append(center)

    return JsonResponse(result)
