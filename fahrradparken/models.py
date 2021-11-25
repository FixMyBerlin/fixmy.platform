from collections import defaultdict
from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
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

    def __str__(self):
        return f"{self.name} ({self.id})"

    @property
    def net_promoter_score(self):
        """
        Returns Net Promoter Score for this station.

        Returns 0 if no ratings exist.
        """
        promoter_count = 0
        detractor_count = 0
        total_count = 0

        for sr in self.survey_responses.all():
            total_count += 1
            if sr.npr >= 9:
                promoter_count += 1
            elif sr.npr <= 6:
                detractor_count += 1

        rating = 0
        try:
            rating = (promoter_count / total_count) - (detractor_count / total_count)
        except ZeroDivisionError:
            pass

        return {
            'rating': rating,
            'total_count': total_count,
            'promoter_count': promoter_count,
            'detractor_count': detractor_count,
        }

    @property
    def annoyances(self):
        """
        Transform survey data on annoyances into a response object.

        The response object contains a key for every existing annoyance. The
        value of that key is the number of times this annoyance has been
        selected in a survey.
        """
        rv = defaultdict(int)
        for sr in self.survey_responses.all():
            for annoyance in sr.annoyances.split(','):
                if len(annoyance) > 0:
                    rv[annoyance] += 1
        return rv

    @property
    def annoyances_custom(self):
        """Return list of written out annoyances."""
        query = self.survey_responses.exclude(annoyance_custom__isnull=True).exclude(
            annoyance_custom__exact=''
        )
        return [sr.annoyance_custom for sr in query.all()]

    @property
    def photos(self):
        """
        Return photos submitted by users for this station.

        Before uploaded photos have been moderated in the Django admin panel
        their URL and description are not returned. If photos are rejected
        during moderation the photo and description should be deleted in the
        Django admin.
        """

        def get_photo_url(key):
            bucket = settings.AWS_STORAGE_BUCKET_NAME
            return f"https://{bucket}.s3.amazonaws.com/{key}"

        query = self.survey_responses.exclude(photo__isnull=True).exclude(
            photo__exact=''
        )

        def get_photo_serialisation(entry):
            if entry.is_photo_published:
                return {
                    'photo_url': get_photo_url(entry.photo),
                    'description': entry.photo_description,
                    'is_published': True,
                }
            else:
                return {'photo_url': None, 'description': None, 'is_published': False}

        return [get_photo_serialisation(sr) for sr in query.all()]

    @property
    def requested_locations(self):
        """Return descriptions of requested locations for parking structures."""
        query = self.survey_responses.exclude(requested_location__isnull=True).exclude(
            requested_location__exact=''
        )
        return [sr.requested_location for sr in query.all()]


class SurveyStation(BaseModel):
    """A survey response about stations."""

    session = models.UUIDField(_('session'))
    station = models.ForeignKey(
        Station, related_name='survey_responses', on_delete=models.CASCADE
    )
    survey_version = models.IntegerField(_('survey version'), default=1)
    npr = models.IntegerField(_('net promoter rating'))
    annoyances = models.CharField(_('annoyances'), max_length=32, blank=True, null=True)
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
    is_photo_published = models.BooleanField(_('photo published'), default=False)

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('session', 'station_id'), name='unique-session-station'
            ),
        )
        verbose_name = _('Station survey')
        verbose_name_plural = _('Station surveys')


class SurveyBicycleUsage(BaseModel):
    """A survey response about bicycle usage."""

    session = models.UUIDField(_('session'), primary_key=True)
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
        (0, _('less than 5 minutes')),
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


class ParkingFacility(BaseModel):
    capacity = models.IntegerField(_('capacity'))
    confirmations = models.PositiveSmallIntegerField(_('confirmations'), default=0)
    covered = models.BooleanField(_('covered'), null=True)
    external_id = models.CharField(
        _('external ID'), max_length=100, blank=True, null=True, unique=True
    )
    location = models.PointField(_('location'), srid=4326)
    parking_garage = models.BooleanField(_('part of parking garage'), null=True)
    secured = models.BooleanField(_('secured'), null=True)
    source = models.CharField(_('source'), max_length=100, blank=True, null=True)
    stands = models.BooleanField(_('stands'), null=True)
    station = models.ForeignKey(
        Station, related_name='parking_facilities', on_delete=models.CASCADE
    )
    two_tier = models.BooleanField(_('two tier'), null=True)

    TYPE_CHOICES = (
        (0, _('enclosed compound')),
        (1, _('bicycle locker')),
        (2, _('bicycle parking tower')),
    )
    type = models.IntegerField(choices=TYPE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name = _('parking facility')
        verbose_name_plural = _('parking facilities')

    @property
    def condition(self):
        return self.parkingfacilitycondition_set.aggregate(Avg('value'))['value__avg']

    @property
    def occupancy(self):
        return self.parkingfacilityoccupancy_set.aggregate(Avg('value'))['value__avg']

    @classmethod
    def next_external_id(cls, station):
        objects = cls.objects.filter(station_id=station.id).all()
        suffixes = [0] + sorted(o.external_id.split('.')[1] for o in objects)
        return f'{station.id}.{suffixes[-1] + 1}'


class ParkingFacilityCondition(models.Model):
    parking_facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE)
    VALUE_CHOICES = (
        (0, _('very bad')),
        (1, _('bad')),
        (2, _('good')),
        (3, _('very good')),
    )
    value = models.IntegerField(choices=VALUE_CHOICES)

    class Meta:
        verbose_name = _('condition')


class ParkingFacilityOccupancy(models.Model):
    parking_facility = models.ForeignKey(ParkingFacility, on_delete=models.CASCADE)
    VALUE_CHOICES = (
        (0, _('overcapacity')),
        (1, _('high')),
        (2, _('medium')),
        (3, _('low')),
    )
    value = models.IntegerField(choices=VALUE_CHOICES)

    class Meta:
        verbose_name = _('occupancy')


class ParkingFacilityPhoto(models.Model):
    parking_facility = models.ForeignKey(
        ParkingFacility, related_name='photos', on_delete=models.CASCADE
    )
    description = models.TextField(_('description'), null=True, blank=True)
    is_published = models.BooleanField(_('is published'), default=False)
    photo_url = models.ImageField(
        _('file'),
        upload_to='fahrradparken/parking-facilities',
    )
    terms_accepted = models.DateTimeField(
        _('upload terms accepted'), null=True, blank=True
    )

    class Meta:
        verbose_name = _('photo')
