from django.http import JsonResponse
from django.core.serializers import serialize
from .models import WorldBorder


def api(request):
    return JsonResponse(serialize(
        'geojson',
        WorldBorder.objects.all(),
        geometry_field='mpoly',
        fields=('name',)), safe=False)
