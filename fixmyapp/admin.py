from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import Edge, PlanningSection, PlanningSectionDetails, Profile


class PlanningSectionAdmin(MarkdownxModelAdmin):
    autocomplete_fields = ('edges',)
    exclude = ('geom_hash',)
    list_display = ('name', 'progress', 'has_updated_edges',)
    list_filter = ('progress',)

    PlanningSection.has_updated_edges.boolean = True
    PlanningSection.has_updated_edges.short_description = 'Has updated edges'

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.geom_hash = form.instance.compute_geom_hash()
        form.instance.save()

    def has_add_permission(self, request):
        return False


class EdgeAdmin(admin.OSMGeoAdmin):
    search_fields = ('elem_nr',)

    def has_add_permission(self, request):
        return False


class ProfileAdmin(admin.ModelAdmin):
    ordering = ('-created_date',)
    list_display = ('id', 'category_of_bike', 'usage', 'created_date')
    list_filter = ('category_of_bike', 'usage')


admin.site.register(Edge, EdgeAdmin)
admin.site.register(PlanningSection, PlanningSectionAdmin)
admin.site.register(PlanningSectionDetails, admin.ModelAdmin)
admin.site.register(Profile, ProfileAdmin)
