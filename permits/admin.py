from django.contrib import admin
from fixmyapp.admin import FMBGeoAdmin

from .models import EventPermit


class FMBPermitsAdmin(FMBGeoAdmin):
    map_template = 'gis/admin/permits/index.html'


class EventPermitAdmin(FMBPermitsAdmin):
    list_display = (
        'id',
        'org_name',
        'category',
        'status',
        'created_date',
        'modified_date',
    )

    order = ['-created_date']
    readonly_fields = (
        'created_date',
        'application_received',
        'application_decided',
        'permit_start',
        'permit_end',
    )


admin.site.register(EventPermit, EventPermitAdmin)
