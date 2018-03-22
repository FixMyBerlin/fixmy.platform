from django.http import JsonResponse
from django.core.serializers import serialize
from .models import Kanten


def api(request):
    return JsonResponse(serialize(
        'geojson',
        Kanten.objects.all()[0:50],
        geometry_field='geom',
        fields=('str_name',)), safe=False)
