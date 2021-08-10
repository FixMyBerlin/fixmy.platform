import uuid
from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _

from fixmyapp.models.base_model import BaseModel


class Signup(BaseModel):
    # personal details
    affiliation = models.CharField(_('affiliation'), max_length=255)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    role = models.CharField(_('role'), max_length=255)
    email = models.CharField(_('email'), max_length=255)
    phone = models.CharField(
        _('telephone number'), max_length=32, null=True, blank=True
    )

    # regarding bicycle parking at their train station
    station_name = models.CharField(_('name of station'), max_length=255)
    message = models.TextField(_('message'), blank=True, null=True)

    newsletter = models.BooleanField(_('requests newsletter'), default=True)


class EventSignup(Signup):
    event_id = models.IntegerField(_('event'))
    event_title = models.CharField(_('event title'), max_length=255)
    event_date = models.CharField(_('event date'), max_length=255)
    event_time = models.CharField(_('event time'), max_length=255)


class Station(BaseModel):
    """A train station."""

    TRAVELLERS_CHOICES = [
        (0, _('No data available')),
        (1, _('less than 100')),
        (2, _('100-300')),
        (3, _('301-1,000')),
        (4, _('1,001-3,000')),
        (5, _('3001-10,000')),
        (6, _('10,001-50,000')),
        (7, _('more than 50,000')),
    ]

    id = models.IntegerField(_('station number'), primary_key=True)
    name = models.CharField(_('name'), max_length=255)
    location = models.PointField(_('geometry'), srid=4326)
    travellers = models.IntegerField(_('traveller count'), choices=TRAVELLERS_CHOICES)
    post_code = models.CharField(_('post code'), max_length=16, blank=True, null=True)
    is_long_distance = models.BooleanField(_('long distance station'), default=False)
    is_light_rail = models.BooleanField(_('light rail station'), default=False)
    is_subway = models.BooleanField(_('subway station'), default=False)
    community = models.CharField(_('community'), max_length=255)

    @property
    def net_promoter_score():
        raise NotImplementedError()

    @property
    def annoyances():
        raise NotImplementedError()

    @property
    def annoyances_custom():
        raise NotImplementedError()

    @property
    def requested_locations():
        raise NotImplementedError()

    @property
    def parking_structures():
        raise NotImplementedError()


class SurveyStation(BaseModel):
    """A survey response about stations."""

    station = models.ForeignKey(
        Station, related_name='survey_responses', on_delete=models.CASCADE
    )
    survey_version = models.IntegerField(default=1)
    npr = models.IntegerField(_('net promoter rating'))
    annoyances = models.CharField(_('annoyances'), max_length=32)
    annoyance_custom = models.CharField(
        _('annoyance custom'), max_length=255, blank=True, null=True
    )
    requested_location = models.CharField(
        _('requested bike parking location'), max_length=255, blank=True, null=True
    )

    def photo_upload_to(instance, filename):
        return f"fahrradparken/stations/{instance.station_id}/{instance.id}"

    photo = models.FileField(
        upload_to=photo_upload_to,
        verbose_name=_("photo"),
        max_length=255,
        null=True,
        blank=True,
    )
    photo_terms_accepted = models.DateTimeField(
        _('photo upload terms accepted'), null=True, blank=True
    )
    photo_description = models.TextField(_('photo description'))
