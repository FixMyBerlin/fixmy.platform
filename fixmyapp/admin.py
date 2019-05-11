from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin
from reversion.admin import VersionAdmin
from .models import (
    Edge,
    Photo,
    Planning,
    PlanningSection,
    PlanningSectionDetails,
    Profile,
    Question,
    Report
)


class PhotoInline(GenericTabularInline):
    extra = 1
    fields = ('src', 'copyright')
    model = Photo


class PlanningAdmin(VersionAdmin):
    autocomplete_fields = ('faq', 'planning_sections')
    inlines = (PhotoInline,)
    list_display = ('project_key', 'title', 'category', 'phase', 'responsible')
    list_filter = ('category', 'phase', 'responsible')
    search_fields = ('planning_sections__edges__str_name', 'project_key')


class PlanningSectionDetailsAdmin(admin.ModelAdmin):
    inlines = (PhotoInline,)
    list_display = ('planning_section', 'side', 'orientation', 'length')
    ordering = ('planning_section',)
    search_fields = ('planning_section__name', 'planning_section__id')

    def has_add_permission(self, request):
        return False


class PlanningSectionAdmin(MarkdownxModelAdmin):
    autocomplete_fields = ('edges',)
    exclude = ('geom_hash',)
    list_display = ('__str__', 'suffix', 'has_plannings', 'has_updated_edges',)
    ordering = ('id',)
    search_fields = ('name', 'id')

    PlanningSection.has_plannings.boolean = True
    PlanningSection.has_updated_edges.boolean = True

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.geom_hash = form.instance.compute_geom_hash()
        form.instance.save()

    def has_add_permission(self, request):
        return False


class EdgeAdmin(admin.OSMGeoAdmin):
    search_fields = ('elem_nr', 'str_name')

    def has_add_permission(self, request):
        return False


class ProfileAdmin(admin.ModelAdmin):
    ordering = ('-created_date',)
    list_display = ('id', 'category_of_bike', 'usage', 'created_date')
    list_filter = ('category_of_bike', 'usage')


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('text',)


class ReportAdmin(admin.OSMGeoAdmin):
    inlines = (PhotoInline,)
    list_display = ('id', 'address', 'subject', 'description', 'created_date')
    ordering = ('-created_date',)

    def subject(self, obj):
        return obj.details['subject']

    def has_add_permission(self, request):
        return False


admin.site.register(Edge, EdgeAdmin)
admin.site.register(Planning, PlanningAdmin)
admin.site.register(PlanningSection, PlanningSectionAdmin)
admin.site.register(PlanningSectionDetails, PlanningSectionDetailsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Report, ReportAdmin)
