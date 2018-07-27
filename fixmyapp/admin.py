from django.contrib.gis import admin
from markdownx.admin import MarkdownxModelAdmin
from .models import (
    CyclingInfrastructurePhoto,
    Edge,
    Planning,
    PlanningPhoto,
    PlanningSection,
    PlanningSectionDetails,
    Profile,
    Question
)


class PlanningPhotoInline(admin.TabularInline):
    model = PlanningPhoto
    readonly_fields = ('height', 'width')
    verbose_name = 'Photo'
    verbose_name_plural = 'Photos'


class PlanningAdmin(admin.ModelAdmin):
    autocomplete_fields = ('faq', 'planning_sections')
    inlines = (PlanningPhotoInline,)
    list_display = ('title',)
    list_filter = ('status',)


class CyclingInfrastructurePhotoInline(admin.TabularInline):
    model = CyclingInfrastructurePhoto
    verbose_name = 'Photo'
    verbose_name_plural = 'Photos'


class PlanningSectionDetailsAdmin(admin.ModelAdmin):
    model = PlanningSectionDetails
    inlines = (CyclingInfrastructurePhotoInline,)


class PlanningSectionAdmin(MarkdownxModelAdmin):
    autocomplete_fields = ('edges',)
    exclude = ('geom_hash',)
    list_display = ('name', 'progress', 'has_updated_edges',)
    list_filter = ('progress',)
    search_fields = ('name',)

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


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('text',)


admin.site.register(Edge, EdgeAdmin)
admin.site.register(Planning, PlanningAdmin)
admin.site.register(PlanningSection, PlanningSectionAdmin)
admin.site.register(PlanningSectionDetails, PlanningSectionDetailsAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Question, QuestionAdmin)
