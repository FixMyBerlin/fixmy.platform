import uuid
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    community = models.CharField(_('community'), max_length=255, null=True, blank=True)

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

    id = models.UUIDField(primary_key=True, editable=False)
    station = models.ForeignKey(
        Station, related_name='survey_responses', on_delete=models.CASCADE
    )
    survey_version = models.IntegerField(_('survey version'), default=1)
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
    photo_description = models.TextField(_('photo description'), null=True, blank=True)


class SurveyBicycleUsage(BaseModel):
    """A survey response about bicycle usage."""

    survey_station = models.ForeignKey(
        SurveyStation, related_name='bicycle_usage', on_delete=models.CASCADE
    )
    survey_version = models.IntegerField(_('survey version'), default=1)

    FREQUENCY_CHOICES = (
        (0, _('(almost) daily')),
        (1, _('1-3 days a week')),
        (2, _('1-3 days a month')),
        (3, _('less than once a month')),
        (4, _('(almost) never')),
    )
    frequency = models.IntegerField(_('frequency'), choices=FREQUENCY_CHOICES)

    reasons = models.CharField(_('reasons'), max_length=32, blank=True)
    reason_custom = models.TextField(_('reasons (free text)'), blank=True)

    DURATION_CHOICES = (
        (0, _('less then 5 minutes')),
        (1, _('5-10 minutes')),
        (2, _('10-15 minutes')),
        (3, _('15-20 minutes')),
        (4, _('20-25 minutes')),
        (5, _('25-30 minutes')),
        (6, _('30 minutes and above')),
    )
    duration = models.IntegerField(_('duration'), choices=DURATION_CHOICES)

    with_children = models.BooleanField(_('with children'))

    PURPOSE_CHOICES = (
        (0, _('work')),
        (1, _('work related')),
        (2, _('education')),
        (3, _('shopping')),
        (4, _('errands')),
        (5, _('leisure')),
        (6, _('transport of persons')),
        (7, _('other')),
    )
    purpose = models.IntegerField(_('purpose'), choices=PURPOSE_CHOICES)

    likert_validators = [
        MinValueValidator(limit_value=0),
        MaxValueValidator(limit_value=5),
    ]

    rating_racks = models.IntegerField(_('bicycle racks'), validators=likert_validators)
    rating_sheltered_racks = models.IntegerField(
        _('sheltered bicycle racks'), validators=likert_validators
    )
    rating_bike_box = models.IntegerField(
        _('bicycle box'), validators=likert_validators
    )
    rating_bike_quality = models.IntegerField(
        _('bicycle quality'), validators=likert_validators
    )
    rating_road_network = models.IntegerField(
        _('road network'), validators=likert_validators
    )
    rating_train_network = models.IntegerField(
        _('train network'), validators=likert_validators
    )
    rating_services = models.IntegerField(_('services'), validators=likert_validators)

    PRICE_CHOICES = (
        (0, _('less than 5€')),
        (1, _('5-10€')),
        (2, _('10-15€')),
        (3, _('15-20€')),
        (4, _('more than 20€')),
    )
    price = models.IntegerField(_('price'), choices=PRICE_CHOICES, null=True)

    AGE_CHOICES = (
        (0, _('under 18')),
        (1, _('18-24')),
        (2, _('25-29')),
        (3, _('30-39')),
        (4, _('40-49')),
        (5, _('50-64')),
        (6, _('65-74')),
        (7, _('75 and above')),
    )
    age = models.IntegerField(_('age'), choices=AGE_CHOICES)