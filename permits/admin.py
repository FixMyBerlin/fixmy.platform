from anymail.exceptions import AnymailError
from django.contrib import admin
from fixmyapp.admin import FMBGeoAdmin
from django.contrib import messages
from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from smtplib import SMTPException

from .models import EventPermit


class FMBPermitsAdmin(FMBGeoAdmin):
    map_template = 'gis/admin/permits/index.html'


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


class EventPermitAdmin(FMBPermitsAdmin):
    list_display = (
        'id',
        'title',
        'category',
        'status',
        'created_date',
        'application_decided',
    )

    list_filter = (
        'status',
        NoticeSentFilter,
        PermitCheckFilter,
        TrafficOrderCheckFilter,
        'category',
    )

    save_on_top = True
    search_fields = ('email', 'org_name', 'last_name', 'title')

    order = ['-created_date']
    readonly_fields = (
        'created_date',
        'application_received',
        'application_decided',
        'permit_start',
        'permit_end',
        'permit',
        'traffic_order',
    )

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

    def send_notices(self, request, queryset):
        """Send acception/rejection notices to applicants"""

        numsent = 0
        for application in queryset:
            if application.status not in [
                EventPermit.STATUS_ACCEPTED,
                EventPermit.STATUS_REJECTED,
            ]:
                continue

            try:
                application.send_notice()
                application.save()
                numsent += 1
            except AttributeError as err:
                if str(err) == "Missing data":
                    self.message_user(
                        request,
                        f"Im Antrag {application.pk} sind nicht alle für den Bescheid nötigen Informationen eingetragen.",
                        messages.ERROR,
                    )
                    continue
                elif str(err) == "Missing note":
                    self.message_user(
                        request,
                        f"Die Ablehnung für {application.title} enthält noch keine Begründung und wurde daher nicht versandt",
                        messages.ERROR,
                    )
                    continue
                elif str(err) == "Campaign missing permit date range":
                    self.message_user(
                        request,
                        f"Der Antrag für {application.title} ist Teil der Kampagne {_(application.campaign)}, für die noch keine Regelzeiträume für die Genehmigungen festgelegt wurden.",
                        messages.ERROR,
                    )
                elif str(err) == "Park zone permit missing park zone selection":
                    self.message_user(
                        request,
                        f"Im Antrag {application.pk} wurde noch kein Grünanlagen-Bereich ausgewählt.",
                        messages.ERROR,
                    )
                    continue
                else:
                    raise
            except (SMTPException, AnymailError) as e:
                self.message_user(
                    request,
                    f"Bescheid für {application.title} konnte nicht versandt werden: {str(e)}",
                    messages.ERROR,
                )

        self.message_user(
            request,
            f"Ein Bescheid wurde an {numsent} Adressaten versandt.",
            messages.SUCCESS if numsent > 0 else messages.WARNING,
        )

    send_notices.short_description = _('send application notices')

    actions = [send_notices]


admin.site.register(EventPermit, EventPermitAdmin)
