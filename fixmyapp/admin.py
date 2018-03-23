from django.contrib.gis import admin
from .models import Kanten, Project


class ProjectAdmin(admin.ModelAdmin):
    autocomplete_fields = ('edges',)


class KantenAdmin(admin.OSMGeoAdmin):
    search_fields = ('elem_nr',)

    def has_add_permission(self, request):
        return False


admin.site.register(Kanten, KantenAdmin)
admin.site.register(Project, ProjectAdmin)
