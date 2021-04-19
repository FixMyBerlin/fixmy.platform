from datetime import datetime, date, timezone, timedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
import uuid

from fixmyapp.models.base_model import BaseModel


class Permit(BaseModel):
    # The applicant has expressed interest in an application
    STATUS_INTERESTED = 'interested'

    # Pending pre-approval of an expression of interest
    STATUS_PREAPPROVAL = 'preapproval'

    # Waiting for the applicant to submit the application form
    STATUS_REGISTRATION = 'waiting_for_application'

    # The application has been submitted
    STATUS_REGISTERED = 'application_received'

    # The application is in the process of verification by administration officials
    STATUS_CONFIRMING = 'application_verification'

    # The application has been approved
    STATUS_ACCEPTED = 'application_accepted'

    # The application has been rejected
    STATUS_REJECTED = 'application_rejected'

    STATUS_CHOICES = (
        (STATUS_INTERESTED, _('expression of interest')),
        (STATUS_PREAPPROVAL, _('preapproval pending')),
        (STATUS_REGISTRATION, _('waiting for application')),
        (STATUS_REGISTERED, _('application received')),
        (STATUS_CONFIRMING, _('application verification')),
        (STATUS_ACCEPTED, _('application accepted')),
        (STATUS_REJECTED, _('application rejected')),
    )

    status = models.CharField(
        _('status'), max_length=64, choices=STATUS_CHOICES, default=STATUS_INTERESTED
    )

    email = models.CharField(_('email'), max_length=255)

    application_received = models.DateTimeField(_('Application received'), null=True)
    application_decided = models.DateTimeField(_('Notice sent'), null=True)

    permit_start = models.DateField(_('Permit valid from'), null=True)
    permit_end = models.DateField(_('Permit valid until'), null=True)

    note = models.TextField(_('note for the registrant'), blank=True)
    note_internal = models.TextField(_('internal note'), blank=True)

    tos_accepted = models.BooleanField(_('tos_accepted'), default=False)
    agreement_accepted = models.BooleanField(_('agreement accepted'), default=False)
    followup_accepted = models.BooleanField(_('follow-up accepted'), default=False)

    class Meta:
        # `Permit` is an abstract base class and cannot be used on its own as a
        # Django model
        abstract = True


class EventPermit(Permit):
    CATEGORY_CHOICES = (
        ('restaurant', _('restaurant')),
        ('retail', _('retail')),
        ('workshop', _('workshop')),
        ('social', _('social')),
        ('other', _('miscellaneous')),
    )

    REGULATION_CHOICES = (
        (0, "Gehweg"),
        (1, "Parken längs"),
        (2, "Parken quer"),
        (3, "Parken diagonal"),
        (4, "Sonstige"),
        (5, "Grünanlagen"),
    )

    CAMPAIGN_CHOICES = [
        ('xhain2021', 'Xhain 2021'),
    ]

    CAMPAIGN_PATHS = {
        'xhain2021': 'friedrichshain-kreuzberg',
    }

    # date constructor uses 1-based month number, i.e. january is 1
    CAMPAIGN_DURATION = {
        'xhain2021': [date(2021, 3, 1), date(2021, 10, 1)],
    }

    campaign = models.CharField(_('campaign'), choices=CAMPAIGN_CHOICES, max_length=32)
    category = models.CharField(
        _('category'), choices=CATEGORY_CHOICES, max_length=255, blank=True, null=True
    )

    permit_checked = models.BooleanField(_('permit checked'), default=False)
    permit_check_note = models.CharField(
        _('permit check notes'), max_length=255, blank=True, null=True
    )
    traffic_order_checked = models.BooleanField(
        _('traffic order checked'), default=False
    )
    traffic_order_check_note = models.CharField(
        _('traffic order check notes'), max_length=255, blank=True, null=True
    )

    org_name = models.CharField(_('organisation name'), max_length=255, blank=True)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    phone = models.CharField(
        _('telephone number'), max_length=32, null=True, blank=True
    )
    address = models.TextField(_('address'))

    date = models.DateField(_('event date'))
    setup_start = models.TimeField(_('setup start time'))
    event_start = models.TimeField(_('event start time'))
    event_end = models.TimeField(_('event end time'))
    teardown_end = models.TimeField(_('teardown end time'))

    NUM_PARTICIPANTS_CHOICES = (
        (0, _("less than 50")),
        (1, _("50 - 200")),
        (2, _("201 - 500")),
    )
    num_participants = models.IntegerField(
        _('number of participants'), choices=NUM_PARTICIPANTS_CHOICES
    )

    LOCATION_PARK = "park"
    LOCATION_PARKING = "parking"
    LOCATION_CATEGORY_CHOICES = (
        (LOCATION_PARK, _("park")),
        (LOCATION_PARKING, _("parking")),
    )
    area_category = models.CharField(
        _("location category"), choices=LOCATION_CATEGORY_CHOICES, max_length=255
    )

    area = models.GeometryField(
        _('installation area'),
        srid=4326,
    )

    AREA_PARK_NAMES = (
        (0, "Mehringdamm 90"),
        (1, "Heilig-Kreuz-Kirche"),
        (2, "Elise-Tilse-Park, Bereich am Hallesches Ufer"),
        (3, "Mariannenplatz, Rondell"),
        (4, "Spreewaldplatz 5/Skalitzer Str."),
        (5, "Spreewaldplatz 5"),
        (6, "Görlitzer Park, Platz vor Pamukkale"),
        (7, "Görlitzer Park, ehem. Görlitzer Tunnel"),
        (8, "Simplonstr. 2, Verkehrsinsel"),
        (9, "Wühlischplatz"),
        (10, "Görlitzer Park, hinter dem Bauwagen Parkläufer"),
        (11, "Görlitzer Park, zw. Pamukkale und Jugendverkehrsschule"),
        (12, "Görlitzer Park, vor Görlitzer Str. 1"),
        (13, "Görlitzer Park, Eingang Skalitzer Str."),
        (14, "Görlitzer Park, Wiese am Sportplatz Wiener Str. 59A"),
        (15, "Görlitzer Park, an der Rodelbahn"),
        (16, "Görlitzer Ufer"),
        (17, "Ratiborstr. 14 b, Studentenbad"),
    )
    area_park_name = models.IntegerField(
        _("location park name"), choices=AREA_PARK_NAMES, null=True, blank=True
    )

    def setup_sketch_upload_to(instance, filename):
        return f"{instance.campaign}/gastro/{instance.id}/sketch"

    setup_sketch = models.FileField(
        upload_to=setup_sketch_upload_to,
        verbose_name=_("setup sketch"),
        null=True,
        blank=True,
    )

    title = models.CharField(_("event title"), max_length=80)
    description = models.TextField(_("event announcement"), max_length=200)
    details = models.TextField(_("event details"), max_length=2000)

    def insurance_upload_to(instance, filename):
        return f"{instance.campaign}/gastro/{instance.id}/insurance"

    insurance = models.FileField(
        upload_to=insurance_upload_to,
        verbose_name=_("proof of insurance"),
    )

    def agreement_upload_to(instance, filename):
        return f"{instance.campaign}/gastro/{instance.id}/agreement"

    agreement = models.FileField(
        upload_to=agreement_upload_to,
        verbose_name=_("event agreement"),
    )

    def public_benefit_upload_to(instance, filename):
        return f"{instance.campaign}/gastro/{instance.id}/public_benefit"

    public_benefit = models.FileField(
        upload_to=public_benefit_upload_to,
        verbose_name=_("proof of public benefit"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('event permit')
        verbose_name_plural = _('event permits')
        ordering = ['campaign', 'title']

    def __str__(self):
        if self.title is not None and len(self.title) > 0:
            return f"{self.id}: {self.title[:16]}"
        return f"{self.id}: Kein Titel"

    @property
    def permit_url(self):
        """Return URL of this application's permit"""
        if self.area_category == self.LOCATION_PARK:
            return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/veranstaltungen/{self.id}/gruenflaechen-genehmigung"
        else:
            return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/veranstaltungen/{self.id}/genehmigung"

    @property
    def traffic_order_url(self):
        """Return URL of this application's traffic order"""
        return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/veranstaltungen/{self.id}/anordnung"

    def send_notice(self):
        """Send notice informing the applicant about being accepted/rejected

        Make sure to save the instance after calling this method as the date of
        the decision is recorded on call.
        """

        if self.status == EventPermit.STATUS_ACCEPTED:
            context = {
                "is_park_zone": self.area_category == EventPermit.LOCATION_PARK,
                "is_parking_zone": self.area_category == EventPermit.LOCATION_PARKING,
                "applicant_email": self.email,
                "link_permit": self.permit_url,
                "link_traffic_order": self.traffic_order_url,
            }
            subject = "Ihr Antrag auf eine Sondernutzung für eine Veranstaltung – Xhain-Terrassen"
            body = render_to_string("xhain/notice_event_accepted.txt", context=context)
        elif self.status == EventPermit.STATUS_REJECTED:
            try:
                context = {
                    "applicant_email": self.email,
                    "application_created": self.created_date.date(),
                    "application_received": self.application_received.date(),
                    "legal_deadline": date.today() + timedelta(days=14),
                    "title": self.title,
                    "full_name": f"{self.first_name} {self.last_name}",
                    "rejection_reason": self.note,
                }
                pass
            except AttributeError:
                raise AttributeError("Missing data")

            if self.note is None or len(self.note) == 0:
                raise AttributeError("Missing note")

            subject = "Ihr Antrag auf eine Sondernutzungserlaubnis Xhain-Terrassen "
            body = render_to_string("xhain/notice_event_rejected.txt", context=context)
        else:
            raise ValueError("Invalid status for sending notice email")

        send_mail(
            subject, body, settings.DEFAULT_FROM_EMAIL, [settings.GASTRO_RECIPIENT]
        )

        try:
            self.set_application_decided()
        except KeyError:
            raise AttributeError("Campaign missing permit date range")

    def set_application_decided(self):
        """Save dates relative to time of application decision"""
        self.application_decided = datetime.now(tz=timezone.utc)
        if self.status == self.STATUS_ACCEPTED:
            campaign_start = self.CAMPAIGN_DURATION[self.campaign][0]
            campaign_end = self.CAMPAIGN_DURATION[self.campaign][1]

            today = datetime.now(tz=timezone.utc).date()

            self.permit_start = today if today > campaign_start else campaign_start
            self.permit_end = campaign_end
