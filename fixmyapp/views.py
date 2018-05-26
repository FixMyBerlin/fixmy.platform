from django.contrib.gis.db.models import Union
from django.http import JsonResponse
from .models import PlanningSection
import json
import random

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
