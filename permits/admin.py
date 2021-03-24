from django.contrib import admin
from fixmyapp.admin import FMBGeoAdmin

from .models import EventPermit


class FMBPermitsAdmin(FMBGeoAdmin):
    map_template = 'gis/admin/permits/index.html'


class EventPermitAdmin(FMBPermitsAdmin):
    pass


admin.site.register(EventPermit, EventPermitAdmin)