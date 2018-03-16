from django.contrib.gis import admin
from .models import WorldBorder


class WorldBorderAdmin(admin.OSMGeoAdmin):
    list_display = ['name', 'pop2005']
    fields = ['name', 'pop2005', 'mpoly']

admin.site.register(WorldBorder, WorldBorderAdmin)
