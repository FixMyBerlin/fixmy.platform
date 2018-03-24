from django.contrib.gis import admin
from .models import Edge, Project


class ProjectAdmin(admin.ModelAdmin):
    autocomplete_fields = ('edges',)


class EdgeAdmin(admin.OSMGeoAdmin):
    search_fields = ('elem_nr',)

    def has_add_permission(self, request):
        return False


admin.site.register(Edge, EdgeAdmin)
admin.site.register(Project, ProjectAdmin)
