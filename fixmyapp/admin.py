from django.contrib.gis import admin
from .models import Kanten, Project

admin.site.register(Kanten, admin.OSMGeoAdmin)
admin.site.register(Project, admin.OSMGeoAdmin)
