from datetime import date, datetime, timezone, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.gis import admin
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import format_html
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
    default_lat = 6_894_699.801_282_43
    default_lon = 1_492_237.774_083_83
    default_zoom = 11


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


class NoticeSentFilter(SimpleListFilter):
    """Filter entries whose application decided date has not been set"""

    title = _('Notice sent')
    parameter_name = 'are_notices_sent'

    def lookups(self, request, model_admin):
        return (('yes', _('Notice sent')), ('no', _('Notice not sent')))

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(application_decided=None)
        elif self.value() == 'no':
            return queryset.filter(application_decided=None)
        else:
            return queryset


class PermitCheckFilter(SimpleListFilter):
    """Filter entries where permit conditions have been checked"""

    title = _('Permit checked')
    parameter_name = 'permit_checked'

    def lookups(self, request, model_admin):
        return (
            ('checked', _('Permit checked')),
            ('unchecked', _('Permit not checked')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'checked':
            return queryset.filter(permit_checked=True)
        elif self.value() == 'unchecked':
            return queryset.exclude(permit_checked=True)
        else:
            return queryset


class TrafficOrderCheckFilter(SimpleListFilter):
    """Filter entries where traffic order conditions have been checked"""

    title = _('Traffic order checked')
    parameter_name = 'traffic_order_checked'

    def lookups(self, request, model_admin):
        return (
            ('checked', _('Traffic order checked')),
            ('unchecked', _('Traffic order not checked')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'checked':
            return queryset.filter(traffic_order_checked=True)
        elif self.value() == 'unchecked':
            return queryset.exclude(traffic_order_checked=True)
        else:
            return queryset


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
    list_filter = (
        'status',
        NoticeSentFilter,
        PermitCheckFilter,
        TrafficOrderCheckFilter,
        'regulation',
        'category',
    )
    ordering = ['-created_date']
    readonly_fields = (
        'created_date',
        'application_received',
        'application_decided',
        'application_form',
        'permit_start',
        'permit_end',
        'permit',
        'renewal_sent_on',
        'renewal_application',
        'traffic_order',
    )
    search_fields = ('shop_name', 'last_name', 'address')
    save_on_top = True

    def application_form(self, obj):
        if obj.pk is None:
            return _('Permalinks are available after saving for the first time')
        return format_html(
            '<a href="'
            + obj.application_form_url
            + '" target="_blank">'
            + obj.application_form_url
            + '</a> <p>(nur einsehbar für die Statusse <em>wartet auf Antrag</em> und <em>Antrag liegt vor</em>)</p>'
        )

    application_form.allow_tags = True
    application_form.short_description = _('application form')

    def renewal_form(self, obj):
        if obj.pk is None:
            return _('Permalinks are available after saving for the first time')
        return format_html(
            '<a href="'
            + obj.renewal_form_url
            + '" target="_blank">'
            + obj.renewal_form_url
            + '</a> <p>(nur einsehbar, nachdem Angebot zum Folgeantrag verschickt wurde)</p>'
        )

    renewal_form.allow_tags = True
    renewal_form.short_description = _('renewal form')

    def permit(self, obj):
        if obj.pk is None:
            return _('Permalinks are available after saving for the first time')
        return format_html(
            '<a href="'
            + obj.permit_url
            + '" target="_blank">'
            + obj.permit_url
            + '</a> <p>(nur einsehbar, wenn Antrag angenommen)</p>'
        )

    permit.allow_tags = True
    permit.short_description = _('permit')

    def traffic_order(self, obj):
        if obj.pk is None:
            return _('Permalinks are available after saving for the first time')
        return format_html(
            '<a href="'
            + obj.traffic_order_url
            + '" target="_blank">'
            + obj.traffic_order_url
            + '</a> <p>(nur einsehbar, wenn Antrag angenommen)</p>'
        )

    traffic_order.allow_tags = True
    traffic_order.short_description = _('traffic order')

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

        numsent = 0
        for application in queryset:
            if application.status == GastroSignup.STATUS_ACCEPTED:
                context = {
                    "is_boardwalk": application.regulation == REGULATION_GEHWEG,
                    "is_restaurant": application.category == 'restaurant',
                    "applicant_email": application.email,
                    "link_permit": application.permit_url,
                    "link_traffic_order": application.traffic_order_url,
                }
                subject = "Ihre Sondergenehmigung - XHainTerrassen"
                body = render_to_string(
                    "gastro/notice_accepted.txt", context=context, request=request
                )
            elif application.status == GastroSignup.STATUS_REJECTED:
                try:
                    context = {
                        "applicant_email": application.email,
                        "application_created": application.application_received.date(),
                        "application_received": application.application_received.date(),
                        "legal_deadline": date.today() + timedelta(days=14),
                        "shop_name": application.shop_name,
                        "full_name": f"{application.first_name} {application.last_name}",
                        "rejection_reason": application.note,
                    }
                except AttributeError:
                    self.message_user(
                        request,
                        f"Im Antrag {application.pk} sind nicht alle für den Bescheid nötigen Informationen eingetragen.",
                        messages.ERROR,
                    )
                    continue

                if application.note is None or len(application.note) == 0:
                    self.message_user(
                        request,
                        f"Die Ablehnung für {application.shop_name} enthält noch keine Begründung und wurde daher nicht versandt",
                        messages.WARNING,
                    )
                    continue

                subject = "Ihr Antrag auf eine Sondernutzungsfläche XHain-Terrassen"
                body = render_to_string(
                    "gastro/notice_rejected.txt", context=context, request=request
                )
            else:
                continue

            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.GASTRO_RECIPIENT],
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    f"Bescheid für {application.shop_name} konnte nicht versandt werden: {e.strerror}",
                    messages.ERROR,
                )
            else:
                try:
                    application.set_application_decided()
                    application.save()
                except KeyError:
                    self.message_user(
                        request,
                        f"Der Antrag für {application.shop_name} ist Teil der Kampagne {_(application.campaign)}, für die noch keine Regelzeiträume für die Genehmigungen festgelegt wurden.",
                    )
                numsent += 1
        self.message_user(
            request,
            f"Ein Bescheid wurde an {numsent} Adressaten versandt.",
            messages.SUCCESS,
        )

    send_notices.short_description = _('send application notices')

    def send_renewal_offer(self, request, queryset):
        """Send offers to apply for a renewal of the application"""
        RENEWAL_CAMPAIGN = 'xhain2'
        numsent = 0
        for application in queryset:
            renewal_campaign_end = GastroSignup.CAMPAIGN_DURATION[RENEWAL_CAMPAIGN][1]
            application_form_url = f"{settings.FRONTEND_URL}/{GastroSignup.CAMPAIGN_PATHS.get(application.campaign)}/terrassen/anmeldung"

            context = {
                "permit_end": application.permit_end,
                "renewal_campaign_end": renewal_campaign_end,
                "renewal_form_url": application.renewal_form_url,
                "application_form_url": application_form_url,
                "sender": "Bezirksamt Friedrichshain-Kreuzberg",
            }

            subject = "Folgeantrag für Sondernutzungsfläche XHain-Terrassen"
            body = render_to_string(
                "gastro/renewal_offer.txt", context=context, request=request
            )

            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.GASTRO_RECIPIENT],
                )
            except SMTPException as e:
                self.message_user(
                    request,
                    f"Bescheid für {application.shop_name} konnte nicht versandt werden: {e.strerror}",
                    messages.ERROR,
                )
            else:
                application.renewal_sent_on = datetime.now(tz=timezone.utc)
                application.save()
                numsent += 1

        self.message_user(
            request,
            f"Ein Angebot zum Folgeantrag wurde an {numsent} Adressaten versandt.",
            messages.SUCCESS,
        )

    send_renewal_offer.short_description = _('send renewal offer')

    actions = [
        mark_signup_verification,
        send_gastro_registration_request,
        send_notices,
        send_renewal_offer,
    ]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionDetails, SectionDetailsAdmin)
admin.site.register(PlaystreetSignup, PlaystreetSignupAdmin)
admin.site.register(GastroSignup, GastroSignupAdmin)
