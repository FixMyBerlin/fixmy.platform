from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from fixmyapp.admin import FMBGeoAdmin, PhotoInline

from .models import Report


def mark_in_progress(modeladmin, request, queryset):
    """Update report status to "in verification" for many items at once"""
    queryset.update(status=Report.STATUS_VERIFICATION)


mark_in_progress.short_description = _('set status to "verification"')


class ReportAdmin(FMBGeoAdmin):
    inlines = (PhotoInline,)
    list_display = ('id', 'address', 'subject', 'description', 'status', 'created_date')
    ordering = ('-created_date',)
    actions = [mark_in_progress]

    def has_add_permission(self, request):
        return False


admin.site.register(Report, ReportAdmin)
