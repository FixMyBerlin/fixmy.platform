from datetime import date, datetime, timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.gis import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import ngettext, gettext_lazy as _
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


class FMBGastroAdmin(FMBGeoAdmin):
    map_template = 'gis/admin/gastro/index.html'


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


class GastroSignupAdmin(FMBGastroAdmin):
    list_display = (
        'id',
        'shop_name',
        'address',
        'regulation',
        'status',
        'created_date',
        'modified_date',
    )
    list_filter = ('status', 'regulation', 'category')
    ordering = ('status', 'created_date')
    readonly_fields = (
        'access_key',
        'created_date',
        'application_received',
        'application_decided',
    )
    search_fields = ('shop_name', 'last_name', 'address')

    def mark_signup_verification(self, request, queryset):
        """Update signup status to in 'in verification'"""
        queryset.update(status=GastroSignup.STATUS_VERIFICATION)
        numaffected = len(queryset)
        self.message_user(
            request,
            ngettext(
                "{numaffected} signup set to 'in verification'",
                "{numaffected} signups set to 'in verification'",
                numaffected,
            ).format(numaffected=numaffected),
            messages.SUCCESS,
        )

    mark_signup_verification.short_description = _('set status to "verification"')

    def send_gastro_registration_request(self, request, queryset):
        """Send registration requests to registrants"""
        numsent = 0
        for signup in queryset:
            subject = 'Ihre Interessensbekundung bei Offene Terrassen für Friedrichshain-Kreuzberg'
            registration_url = f"https://fixmyberlin.de/friedrichshain-kreuzberg/terrassen/registrierung/{signup.id}/{signup.access_key}"
            body = f'''Sehr geehrte Damen und Herren,

Vielen Dank für Ihre Meldung. Um einen formalen Antrag auf Nutzung einer
Sonderfläche zu stellen bitten wir Sie, Ihre Angaben unter folgendem, für sie
personalisierten Link zu ergänzen:

Der Link funktioniert nur für die Antragstellung Ihres Betriebs, bitte geben Sie
den Link nicht an Dritte weiter, um einen Missbrauch zu vermeiden. Alle Anträge
werden nach Eingangsdatum bearbeitet, bitte rechnen Sie mit einigen Tagen Bearbeitungszeit.
Sobald Ihr Antrag bewilligt oder abgelehnt wurde, erhalten Sie eine weitere E-Mail.
Bitte halten Sie für die Registrierung eine Kopie oder ein Foto Ihrer
Gewerbeanmeldung (1. Seite) bereit.

{registration_url}

Wir hoffen, dass wir Ihren Betrieb mit dieser Maßnahme in diesen wirtschaftlich
schwierigen Zeiten unterstützen können.

Mit freundlichen Grüßen,
Ihr Bezirksamt Friedrichshain-Kreuzberg'''
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [signup.email])
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

    def send_notices(self, request, queryset):
        """Send acception/rejection notices to applicants"""
        REGULATION_GEHWEG = 10
        GENERIC_RECIPIENT = "aufsicht.sga@ba-fk.berlin.de"

        numsent = 0
        for application in queryset:
            if application.status == GastroSignup.STATUS_ACCEPTED:
                context = {
                    "is_boardwalk": application.regulation == REGULATION_GEHWEG,
                    "applicant_email": application.email,
                    "link_permit": application.get_permit_url(),
                    "link_traffic_order": application.get_traffic_order_url(),
                }
                subject = "Ihre Sondergenehmigung - XHainTerrassen"
                body = render_to_string(
                    "gastro/notice_accepted.txt", context=context, request=request
                )

                try:
                    send_mail(
                        subject, body, settings.DEFAULT_FROM_EMAIL, [GENERIC_RECIPIENT]
                    )
                except SMTPException as e:
                    self.message_user(
                        request,
                        f"Benachrichtigung für {application.shop_name} konnte nicht versandt werden: {e.strerror}",
                        messages.ERROR,
                    )
                else:
                    application.application_decided = datetime.now(tz=timezone.utc)
                    application.save()
                    numsent += 1
        self.message_user(
            request,
            f"Benachrichtigung wurde an {numsent} Adressaten versandt.",
            messages.SUCCESS,
        )

    send_notices.short_description = _('send application notices')

    actions = [mark_signup_verification, send_gastro_registration_request, send_notices]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionDetails, SectionDetailsAdmin)
admin.site.register(PlaystreetSignup, PlaystreetSignupAdmin)
admin.site.register(GastroSignup, GastroSignupAdmin)
