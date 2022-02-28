from datetime import datetime, date, timezone, timedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
import uuid

from .base_model import BaseModel


def get_upload_path(instance, filename):
    """Determine the upload path for certificate files"""
    return f"{instance.campaign}/gastro/{instance.id}/{filename}"


class GastroSignup(BaseModel):
    STATUS_NEW = 'new'
    STATUS_VERIFICATION = 'verification'
    STATUS_REGISTRATION = 'waiting_for_application'
    STATUS_REGISTERED = 'application_received'
    STATUS_CONFIRMING = 'application_verification'
    STATUS_ACCEPTED = 'application_accepted'
    STATUS_REJECTED = 'application_rejected'

    STATUS_CHOICES = (
        (STATUS_NEW, _('new')),
        (STATUS_VERIFICATION, _('verification')),
        (STATUS_REGISTRATION, _('waiting for application')),
        (STATUS_REGISTERED, _('application received')),
        (STATUS_CONFIRMING, _('application verification')),
        (STATUS_ACCEPTED, _('application accepted')),
        (STATUS_REJECTED, _('application rejected')),
    )

    CATEGORY_CHOICES = (
        ('restaurant', _('restaurant')),
        ('retail', _('retail')),
        ('workshop', _('workshop')),
        ('social', _('social')),
        ('other', _('miscellaneous')),
    )

    REGULATION_CHOICES = (
        (0, "Parkplatz"),
        (1, "Zone 1: Dresdener Straße 13-20"),
        (2, "Zone 2: Dresdener Straße 119-124"),
        (3, "Zone 3: Simon-Dach-Straße 6-14"),
        (4, "Zone 4: Simon-Dach-Straße 35-41a"),
        (5, "Zone 5: Gabriel-Max-Straße 1-5"),
        (6, "Zone 6: Gabriel-Max-Straße 15-21"),
        (7, "Zone 7: Krossener Straße 11-21"),
        (8, "Zone 8: Grünberger Straße 73-79"),
        (9, "Zone 9: Samariterstraße 34a-37"),
        (10, "Gehweg"),
        (11, "Parken längs"),
        (12, "Parken quer"),
        (13, "Parken diagonal"),
        (14, "Sonstige"),
    )

    TIME_WEEKEND = 'weekend'
    TIME_WORKDAYS = 'workdays'
    TIME_WHOLE_WEEK = 'whole_week'

    TIME_CHOICES = (
        (TIME_WEEKEND, _('weekend')),
        (TIME_WORKDAYS, _('workdays')),
        (TIME_WHOLE_WEEK, _('whole week')),
    )

    CAMPAIGN_CHOICES = [
        ('xhain', 'Xhain Mai 2020'),
        ('xhain2', 'Xhain Juli 2020'),
        ('xhain3', 'Xhain Verlängerungen ab Sep 2020'),
        ('xhain2021', 'Xhain 2021'),
        ('xhain2022', 'Xhain 2022'),
        ('tempelberg', 'Tempelhof-Schöneberg 2020'),
    ]

    # This becomes part of the URLs that are sent to applicants when their
    # applications are granted
    CAMPAIGN_PATHS = {
        'xhain': 'friedrichshain-kreuzberg',
        'xhain2': 'friedrichshain-kreuzberg',
        'xhain3': 'friedrichshain-kreuzberg',
        'xhain2021': 'friedrichshain-kreuzberg',
        'xhain2022': 'friedrichshain-kreuzberg',
        'tempelberg': 'tempelhof-schoeneberg',
    }

    # date constructor uses 1-based month number, i.e. january is 1
    CAMPAIGN_DURATION = {
        'xhain': [date(2020, 6, 23), date(2020, 8, 31)],
        'xhain2': [date(2020, 7, 16), date(2020, 10, 31)],
        'xhain3': [date(2020, 8, 31), date(2020, 10, 31)],
        'xhain2021': [date(2021, 3, 1), date(2021, 12, 31)],
        'xhain2022': [date(2022, 3, 14), date(2022, 10, 31)],
        'tempelberg': None,
    }

    # Maps campaigns to the campaign that a renewal will be created in.
    # Maps to None if renewal is not possible.
    RENEWAL_CAMPAIGN = {
        'xhain': 'xhain3',
        'xhain2': None,
        'xhain3': None,
        'xhain2021': None,
        'xhain2022': None,
    }

    campaign = models.CharField(_('campaign'), choices=CAMPAIGN_CHOICES, max_length=32)
    status = models.CharField(
        _('status'), max_length=64, choices=STATUS_CHOICES, default=STATUS_NEW
    )
    regulation = models.IntegerField(
        _('regulation'), choices=REGULATION_CHOICES, default=0
    )
    opening_hours = models.CharField(
        _('opening hours'), max_length=32, choices=TIME_CHOICES
    )
    category = models.CharField(_('category'), choices=CATEGORY_CHOICES, max_length=255)

    application_received = models.DateTimeField(_('Application received'), null=True)
    application_decided = models.DateTimeField(_('Notice sent'), null=True)

    permit_start = models.DateField(_('Permit valid from'), null=True)
    permit_end = models.DateField(_('Permit valid until'), null=True)

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

    fee_paid = models.BooleanField(_('fee paid'), default=False)
    invoice_number = models.CharField(
        _('invoice number'), max_length=13, blank=True, null=True
    )

    shop_name = models.CharField(_('shop name'), max_length=255)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    email = models.CharField(_('email'), max_length=255)
    phone = models.CharField(
        _('telephone number'), max_length=32, null=True, blank=True
    )
    usage = models.TextField(_('usage'), null=True, blank=True)
    address = models.TextField(_('address'))
    shopfront_length = models.PositiveIntegerField(_('shopfront length'))
    geometry = models.PointField(_('location'), srid=4326)

    area = models.GeometryField(
        _('installation area'), srid=4326, null=True, blank=True
    )

    certificate = models.FileField(
        upload_to=get_upload_path,
        verbose_name=_('registration certificate'),
        max_length=255,
        null=True,
        blank=True,
    )

    tos_accepted = models.BooleanField(_('tos_accepted'), default=False)
    agreement_accepted = models.BooleanField(_('agreement accepted'), default=False)
    followup_accepted = models.BooleanField(_('follow-up accepted'), default=False)

    # Access key for using approved signup data to send in a proper
    # application
    access_key = models.UUIDField(default=uuid.uuid4, editable=False)

    note = models.TextField(_('note for the registrant'), blank=True)
    note_internal = models.TextField(_('internal note'), blank=True)

    # Access key for applying for a renewal of the permit
    access_key_renewal = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True
    )
    renewal_sent_on = models.DateTimeField(
        _('offer to apply for renewal sent on'), null=True, blank=True
    )
    renewal_application = models.ForeignKey(
        'self',
        verbose_name=_('renewal application'),
        related_name='previous_application',
        editable=False,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _('gastro_signup')
        verbose_name_plural = _('gastro_signups')
        ordering = ['campaign', 'address']

    def __str__(self):
        if self.shop_name is not None and len(self.shop_name) > 0:
            return f"{self.id}: {self.shop_name}"
        return f"{self.id}: Kein Betriebsname"

    @property
    def permit_url(self):
        """Return URL of this application's permit"""
        return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/terrassen/verzeichnis/{self.id}/genehmigung"

    @property
    def traffic_order_url(self):
        """Return URL of this application's traffic order"""
        return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/terrassen/verzeichnis/{self.id}/anordnung"

    @property
    def application_form_url(self):
        """Return URL of this application's signup form"""
        return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/terrassen/registrierung/{self.id}/{self.access_key}"

    @property
    def renewal_form_url(self):
        """Return URL where applicants can apply for a renewal of the permit"""
        return f"{settings.FRONTEND_URL}/{self.CAMPAIGN_PATHS.get(self.campaign)}/terrassen/folgeantrag/{self.id}/{self.access_key_renewal}"

    def send_notice(self):
        """Send notice informing the applicant about being accepted/rejected

        Make sure to save the instance after calling this method as the date of
        the decision is recorded on call.
        """
        REGULATION_GEHWEG = 10

        if self.status == GastroSignup.STATUS_ACCEPTED:
            context = {
                "is_boardwalk": self.regulation == REGULATION_GEHWEG,
                "is_restaurant": self.category == 'restaurant',
                "applicant_email": self.email,
                "link_permit": self.permit_url,
                "link_traffic_order": self.traffic_order_url,
            }
            subject = "Ihre Sondergenehmigung - Xhain-Terrassen"
            body = render_to_string("gastro/notice_accepted.txt", context=context)
        elif self.status == GastroSignup.STATUS_REJECTED:
            try:
                context = {
                    "applicant_email": self.email,
                    "application_created": self.application_received.date(),
                    "application_received": self.application_received.date(),
                    "legal_deadline": date.today() + timedelta(days=14),
                    "shop_name": self.shop_name,
                    "full_name": f"{self.first_name} {self.last_name}",
                    "rejection_reason": self.note,
                }
            except AttributeError:
                raise AttributeError("Missing data")

            if self.note is None or len(self.note) == 0:
                raise AttributeError("Missing note")

            subject = "Ihr Antrag auf eine Sondernutzungsfläche Xhain-Terrassen"
            body = render_to_string("gastro/notice_rejected.txt", context=context)
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
