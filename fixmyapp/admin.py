from datetime import date
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.gis import admin
from django.utils.translation import gettext_lazy as _
from reversion.admin import VersionAdmin
from smtplib import SMTPException

from .models import (
    GastroSignup,
    PlaystreetSignup,
    Photo,
    Profile,
    Project,
    Question,
    Report,
    Section,
    SectionDetails,
)


class FMBGeoAdmin(admin.OSMGeoAdmin):
    map_template = 'gis/admin/osm-fmb.html'
    map_width = 800
    map_height = 600


class PhotoInline(GenericTabularInline):
    extra = 1
    fields = ('src', 'copyright')
    model = Photo


class AlertDateFilter(SimpleListFilter):
    title = _('alert date')
    parameter_name = 'alert'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (('exceeded', _('exceeded')),)

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == 'exceeded':
            return queryset.filter(alert_date__lte=date.today())


class ProjectAdmin(FMBGeoAdmin, VersionAdmin):
    autocomplete_fields = ('faq',)
    inlines = (PhotoInline,)
    list_display = (
        'project_key',
        'title',
        'street_name',
        'category',
        'phase',
        'responsible',
        'alert_date',
    )
    list_filter = (AlertDateFilter, 'category', 'phase', 'responsible')
    search_fields = ('project_key', 'street_name')


class SectionDetailsAdmin(admin.ModelAdmin):
    inlines = (PhotoInline,)
    list_display = ('section', 'side', 'orientation', 'length')
    ordering = ('section',)
    search_fields = ('section__name', 'section__id')

    def has_add_permission(self, request):
        return False


class SectionAdmin(FMBGeoAdmin):
    list_display = ('street_name', 'suffix', 'borough')
    ordering = ('id',)
    search_fields = ('street_name', 'id')

    def has_add_permission(self, request):
        return False


class ProfileAdmin(admin.ModelAdmin):
    ordering = ('-created_date',)
    list_display = ('id', 'category_of_bike', 'usage', 'created_date')
    list_filter = ('category_of_bike', 'usage')


class QuestionAdmin(admin.ModelAdmin):
    search_fields = ('text',)


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


class PlaystreetSignupAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign', 'street', 'captain', 'created_date')
    ordering = ('campaign', 'street', 'created_date')


class GastroSignupAdmin(FMBGeoAdmin):
    list_display = ('shop_name', 'category', 'address', 'regulation', 'status')
    list_filter = ('status', 'regulation', 'category')
    ordering = ('campaign', 'regulation', 'address')
    readonly_fields = ('access_key',)

    def mark_signup_verification(self, request, queryset):
        """Update signup status to in 'in verification'"""
        queryset.update(status=GastroSignup.STATUS_VERIFICATION)

    mark_in_progress.short_description = _('set status to "verification"')

    def send_gastro_registration_request(self, request, queryset):
        """Send registration requests to registrants"""
        numsent = 0
        for signup in queryset:
            sender = 'hello@fixmyberlin.de'
            subject = 'Ihre Interessensbekundung bei Offene Terrassen für Friedrichshain-Kreuzberg'
            registration_url = f"https://fixmyberlin.de/friedrichshain-kreuzberg/terrassen/registrierung/{signup.id}/{signup.access_key}"
            body = f'''Sehr geehrte Damen und Herren,

Sie haben einen Bedarf für eine temporäre Erweiterung der Außenflächen
Ihres Gewerbes, Einzelhandels oder sozialen Projektes angemeldet.

Vielen Dank dafür. Für den nächsten Schritt bitten wir Sie, Ihre Angaben
unter folgendem für sie personalisierten Link bis zum Montag, den 1.Juni 2020
zu ergänzen.

Bitte geben Sie diesen Link nicht an Dritte weiter.

{registration_url}

Mit freundlichen Grüßen,
Ihr Bezirksamt Friedrichshain-Kreuzberg'''
            try:
                send_mail(subject, body, sender, [signup.email])
            except SMTPException as e:
                self.message_user(
                    request,
                    f"Antragsformular für {signup.shop_name} konnte nicht versandt werden: {e.strerror}",
                    messages.ERROR,
                )
            else:
                numsent += 1
                signup.status = GastroSignup.STATUS_REGISTRATION
                signup.save()
        self.message_user(
            request,
            f"Antragsformular wurde an {numsent} Adressaten versandt.",
            messages.SUCCESS,
        )

    send_gastro_registration_request.short_description = _('send registation requests')

    actions = [mark_signup_verification, send_gastro_registration_request]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionDetails, SectionDetailsAdmin)
admin.site.register(PlaystreetSignup, PlaystreetSignupAdmin)
admin.site.register(GastroSignup, GastroSignupAdmin)
