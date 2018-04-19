from django.contrib.gis import admin
from .models import Edge, PlanningSection


class PlanningSectionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('edges',)
    exclude = ('geom_hash',)
    list_display = ('name', 'has_updated_edges',)

    PlanningSection.has_updated_edges.boolean = True
    PlanningSection.has_updated_edges.short_description = 'Has updated edges'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.geom_hash = form.instance.compute_geom_hash()
        form.instance.save()


class EdgeAdmin(admin.OSMGeoAdmin):
    search_fields = ('elem_nr',)

    def has_add_permission(self, request):
        return False


admin.site.register(Edge, EdgeAdmin)
admin.site.register(PlanningSection, PlanningSectionAdmin)
