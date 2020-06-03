from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _
from markdownx.models import MarkdownxField
import decimal
import uuid


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Section(BaseModel):
    street_name = models.CharField(_('street name'), max_length=100)
    suffix = models.CharField(_('suffix'), blank=True, null=True, max_length=3)
    borough = models.CharField(_('borough'), blank=True, null=True, max_length=255)
    street_category = models.PositiveSmallIntegerField(_('street category'), null=True)
    geometry = models.MultiLineStringField(_('geometry'), srid=4326, null=True)

    class Meta:
        verbose_name = _('section')
        verbose_name_plural = _('sections')

    def velocity_index(self):
        if len(self.details.all()) > 0:
            return sum(d.velocity_index() for d in self.details.all()) / len(
                self.details.all()
            )
        else:
            return 0

    def safety_index(self):
        if len(self.details.all()) > 0:
            return sum(d.safety_index() for d in self.details.all()) / len(
                self.details.all()
            )
        else:
            return 0

    def __str__(self):
        return '{} ({})'.format(self.street_name, self.id)


class Question(BaseModel):
    text = models.CharField(max_length=256)
    answer = MarkdownxField()

    class Meta:
        verbose_name = _('question')
        verbose_name_plural = _('questions')
        ordering = ('text',)

    def __str__(self):
        return self.text


class Photo(BaseModel):
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    copyright = models.CharField(_('copyright'), blank=True, null=True, max_length=256)
    object_id = models.PositiveIntegerField()
    src = models.ImageField(upload_to='photos', verbose_name=_('file'))

    class Meta:
        verbose_name = _('photo')
        verbose_name_plural = _('photos')

    def __str__(self):
        return self.src.name.split('/')[-1]


class Like(BaseModel):
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class SectionDetails(BaseModel):
    RIGHT = 0
    LEFT = 1
    SIDE_CHOICES = ((RIGHT, _('right')), (LEFT, _('left')))
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
    ORIENTATION_CHOICES = (
        (NORTH, _('north')),
        (EAST, _('east')),
        (SOUTH, _('south')),
        (WEST, _('west')),
    )
    AVG_WIDTH_CROSSINGS = 6
    CI_RATIO_MIN = 0.65

    section = models.ForeignKey(
        Section, related_name='details', on_delete=models.CASCADE
    )
    side = models.PositiveSmallIntegerField(_('side'), choices=SIDE_CHOICES)
    speed_limit = models.PositiveSmallIntegerField(_('speed limit'))
    daily_traffic = models.DecimalField(
        _('daily traffic'), max_digits=8, decimal_places=2
    )
    daily_traffic_heavy = models.DecimalField(
        _('daily traffic heavy'), max_digits=8, decimal_places=2
    )
    daily_traffic_cargo = models.DecimalField(
        _('daily traffic cargo'), max_digits=8, decimal_places=2
    )
    daily_traffic_bus = models.DecimalField(
        _('daily traffic bus'), max_digits=8, decimal_places=2
    )
    length = models.DecimalField(_('length'), max_digits=8, decimal_places=2)
    crossings = models.PositiveSmallIntegerField(_('crossings'))
    orientation = models.CharField(
        _('orientation'), max_length=1, choices=ORIENTATION_CHOICES
    )
    rva1 = models.DecimalField(max_digits=16, decimal_places=12)
    rva2 = models.DecimalField(max_digits=16, decimal_places=12)
    rva3 = models.DecimalField(max_digits=16, decimal_places=12)
    rva4 = models.DecimalField(max_digits=16, decimal_places=12)
    rva5 = models.DecimalField(max_digits=16, decimal_places=12)
    rva6 = models.DecimalField(max_digits=16, decimal_places=12)
    rva7 = models.DecimalField(max_digits=16, decimal_places=12)
    rva8 = models.DecimalField(max_digits=16, decimal_places=12)
    rva9 = models.DecimalField(max_digits=16, decimal_places=12)
    rva10 = models.DecimalField(max_digits=16, decimal_places=12)
    rva11 = models.DecimalField(max_digits=16, decimal_places=12)
    rva12 = models.DecimalField(max_digits=16, decimal_places=12)
    rva13 = models.DecimalField(max_digits=16, decimal_places=12)
    photos = GenericRelation(Photo)

    class Meta:
        verbose_name = _('Section details')
        verbose_name_plural = _('Section details')

    def happy_bike_index(self):
        return self.velocity_index() + self.safety_index()

    def velocity_index(self):
        weighted_sum = sum(
            [
                self.rva3 * 2,
                self.rva4 * 1,
                self.rva7 * 2,
                self.rva8 * 3,
                self.rva9 * 3,
                self.rva10 * 3,
                self.rva11 * 2,
                self.rva12 * 3,
                self.rva13 * 2,
            ]
        )

        if self.cycling_infrastructure_sum() > 0:
            ci_factor = weighted_sum / (self.cycling_infrastructure_sum() * 3)
        else:
            ci_factor = decimal.Decimal(weighted_sum / 3)

        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            return self.cycling_infrastructure_ratio() * ci_factor + (
                1 - self.cycling_infrastructure_ratio()
            )
        else:
            return ci_factor

    def safety_index(self):
        offset = decimal.Decimal(3)
        ci_safety = self.cycling_infrastructure_safety()

        if ci_safety <= self.road_type():
            return (offset + ci_safety - self.road_type()) * decimal.Decimal('2.25')
        else:
            return (offset + (ci_safety - self.road_type()) / 3) * decimal.Decimal(
                '2.25'
            )

    def length_without_crossings(self):
        """Returns length of section without crossings

        We do not count crossings as cycling infrastructure.
        """
        return self.length - self.AVG_WIDTH_CROSSINGS * self.crossings

    def cycling_infrastructure_sum(self):
        """Returns the length of all cycling infrastructure

        Some fields are ignored because we do not count them as cycling
        infrastructure.
        """
        return sum(
            [
                self.rva3,
                self.rva4,
                self.rva5,
                self.rva6,
                self.rva7,
                self.rva8,
                self.rva9,
                self.rva10,
                self.rva11,
                self.rva12,
                self.rva13,
            ]
        )

    def bike_path_sum(self):
        """Returns the length of all bike paths

        Bike paths are paths with their own right of way dedicated to cycling,
        though in many cases shared with pedestrians and other non-motorized
        traffic.
        """
        return sum([self.rva3, self.rva4, self.rva10])

    def shared_use_path_sum(self):
        """Returns the length of all shared use paths

        A shared use path supports multiple modes, such as walking, bicycling,
        inline skating and people in wheelchairs.
        """
        return sum([self.rva5, self.rva6])

    def bike_lane_sum(self):
        """Returns the length of all bike lanes

        Bike lanes or cycle lanes, are on-road lanes marked with paint
        dedicated to cycling and typically excluding all motorized traffic.
        """
        return self.rva7

    def protected_bike_lane_sum(self):
        """Returns the length of all protected bike lanes

        A cycle track, also called separated bike lane or protected bike lane,
        is a physically marked and separated lane dedicated for cycling that is
        on or directly adjacent to the roadway but typically excludes all
        motorized traffic with some sort of vertical barrier.
        """
        return sum([self.rva8, self.rva9])

    def advisory_bike_lane_sum(self):
        """Returns the length of all advisory bike lanes

        An advisory bike lane is a roadway striping configuration which
        provides for two-way motor vehicle and bicycle traffic using a central
        vehicular travel lane and “advisory” bike lanes on either side.
        """
        return sum([self.rva11, self.rva12, self.rva13])

    def cycling_infrastructure_ratio(self):
        return self.cycling_infrastructure_sum() / self.length_without_crossings()

    def bike_path_ratio(self):
        return self._ci_category_ratio(self.bike_path_sum())

    def shared_use_path_ratio(self):
        return self._ci_category_ratio(self.shared_use_path_sum())

    def bike_lane_ratio(self):
        return self._ci_category_ratio(self.bike_lane_sum())

    def protected_bike_lane_ratio(self):
        return self._ci_category_ratio(self.protected_bike_lane_sum())

    def advisory_bike_lane_ratio(self):
        return self._ci_category_ratio(self.advisory_bike_lane_sum())

    def road_type(self):
        """Returns a number categorizing traffic intensity"""

        if self.speed_limit <= 20:
            l = (11000, 18000, 20000)
        elif self.speed_limit <= 30:
            l = (8000, 18000, 20000)
        elif self.speed_limit <= 40:
            l = (6000, 16000, 19000)
        elif self.speed_limit <= 50:
            l = (4000, 10000, 18000)
        elif self.speed_limit <= 60:
            l = (2000, 5000, 7000)
        else:
            l = (2000, 3000, 6000)

        if self.daily_traffic <= l[0]:
            return self.daily_traffic / l[0]
        elif self.daily_traffic <= l[1]:
            return 1 + (self.daily_traffic - l[0]) / (l[1] - l[0])
        elif self.daily_traffic <= l[2]:
            return 2 + (self.daily_traffic - l[1]) / (l[2] - l[1])
        else:
            return 3

    def cycling_infrastructure_safety(self):
        weighted_sum = sum(
            [
                self.rva3 * 3,
                self.rva4 * 3,
                self.rva5 * 3,
                self.rva6 * 3,
                self.rva7 * 2,
                self.rva8 * 3,
                self.rva9 * 3,
                self.rva10 * 3,
                self.rva11 * 1,
                self.rva12 * 1,
                self.rva13 * 1,
            ]
        )
        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            safety = 0
        else:
            safety = weighted_sum / self.cycling_infrastructure_sum()
        return safety

    def _ci_category_ratio(self, category_sum):
        if self.cycling_infrastructure_ratio() < 0.1:
            ratio = 0.0
        else:
            ratio = category_sum / self.length_without_crossings()
        return ratio

    def __str__(self):
        return '{} {}'.format(self.section, self.SIDE_CHOICES[self.side][1])


class Project(BaseModel):
    CATEGORY_NEW_INFRASTRUCTURE = 'new cycling infrastructure'
    CATEGORY_RENOVATION = 'renovation of cycling infrastructure'
    CATEGORY_BIKE_STREET = 'bike street'
    CATEGORY_MODIFICATION_OF_JUNCTION = 'modification of junction'
    CATEGORY_BIKE_PARKING = 'bike parking'
    CATEGORY_CROSSING_AID = 'crossing aid'
    CATEGORY_MODIFICATION_OF_CROSS_SECTION = 'modification of cross section'
    CATEGORY_NEW_STREET = 'new street'
    CATEGORY_SHARED_SPACE = 'shared space'
    CATEGORY_MISCELLANEOUS = 'miscellaneous'

    CATEGORY_CHOICES = (
        (CATEGORY_NEW_INFRASTRUCTURE, _('new cycling infrastructure')),
        (CATEGORY_RENOVATION, _('renovation of cycling infrastructure')),
        (CATEGORY_BIKE_STREET, _('bike street')),
        (CATEGORY_MODIFICATION_OF_JUNCTION, _('modification of junction')),
        (CATEGORY_BIKE_PARKING, _('bike parking')),
        (CATEGORY_CROSSING_AID, _('crossing aid')),
        (CATEGORY_MODIFICATION_OF_CROSS_SECTION, _('modification of cross section')),
        (CATEGORY_NEW_STREET, _('new street')),
        (CATEGORY_SHARED_SPACE, _('shared space')),
        (CATEGORY_MISCELLANEOUS, _('miscellaneous')),
    )

    PHASE_DRAFT = 'draft'
    PHASE_PLANNING = 'planning'
    PHASE_REVIEW = 'review'
    PHASE_INACTIVE = 'inactive'
    PHASE_EXECUTION = 'execution'
    PHASE_READY = 'ready'
    PHASE_MISCELLANEOUS = 'miscellaneous'

    PHASE_CHOICES = (
        (PHASE_DRAFT, _('draft')),
        (PHASE_PLANNING, _('planning')),
        (PHASE_REVIEW, _('review')),
        (PHASE_INACTIVE, _('inactive')),
        (PHASE_EXECUTION, _('execution')),
        (PHASE_READY, _('ready')),
        (PHASE_MISCELLANEOUS, _('miscellaneous')),
    )

    STATUS_UNKNOWN = 'unknown'
    STATUS_IDEA = 'idea'
    STATUS_PRELIMINARY_PLANNING = 'preliminary planning'
    STATUS_BLUEPRINT_PLANNING = 'blueprint planning'
    STATUS_APPROVAL_PLANNING = 'approval planning'
    STATUS_EXAMINATION = 'examination'
    STATUS_EXECUTION_PLANNING = 'execution planning'
    STATUS_PREPARATION_OF_AWARDING = 'preparation of awarding'
    STATUS_AWARDING = 'awarding'
    STATUS_APPLICATION_FOR_CONSTRUCTION_SITE = 'application for construction site'
    STATUS_EXECUTION_OF_CONSTRUCTION_WORK = 'execution of construction work'
    STATUS_READY = 'ready'
    STATUS_REVIEW = 'review'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_UNKNOWN, _('unknown')),
        (STATUS_IDEA, _('idea')),
        (STATUS_PRELIMINARY_PLANNING, _('preliminary planning')),
        (STATUS_BLUEPRINT_PLANNING, _('blueprint planning')),
        (STATUS_APPROVAL_PLANNING, _('approval planning')),
        (STATUS_EXAMINATION, _('examination')),
        (STATUS_EXECUTION_PLANNING, _('execution planning')),
        (STATUS_PREPARATION_OF_AWARDING, _('preparation of awarding')),
        (STATUS_AWARDING, _('awarding')),
        (
            STATUS_APPLICATION_FOR_CONSTRUCTION_SITE,
            _('application for construction site'),
        ),
        (STATUS_EXECUTION_OF_CONSTRUCTION_WORK, _('execution of construction work')),
        (STATUS_READY, _('ready')),
        (STATUS_REVIEW, _('review')),
        (STATUS_CANCELLED, _('cancelled')),
    )

    RIGHT = 0
    LEFT = 1
    BOTH = 2
    SIDE_CHOICES = ((RIGHT, _('right')), (LEFT, _('left')), (BOTH, _('both')))

    TRANSFORM_EPSG_3035 = 3035

    project_key = models.CharField(_('project key'), max_length=100, unique=True)
    published = models.BooleanField(_('published'), default=True)
    title = models.CharField(_('title'), max_length=256)
    side = models.PositiveSmallIntegerField(_('side'), choices=SIDE_CHOICES)
    responsible = models.CharField(_('responsible'), max_length=256)
    description = MarkdownxField(_('description'))
    short_description = models.CharField(
        _('short description'), blank=True, null=True, max_length=200
    )
    geometry = models.GeometryField(_('geometry'), blank=True, null=True)
    category = models.CharField(
        _('category'), blank=True, null=True, max_length=40, choices=CATEGORY_CHOICES
    )
    street_name = models.CharField(_('street name'), max_length=100)
    borough = models.CharField(_('borough'), blank=True, null=True, max_length=255)
    costs = models.PositiveIntegerField(_('costs'), blank=True, null=True)
    draft_submitted = models.CharField(
        _('draft submitted'), blank=True, null=True, max_length=100
    )
    construction_started = models.CharField(
        _('construction started'), blank=True, null=True, max_length=100
    )
    construction_completed = models.CharField(
        _('construction completed'),
        blank=True,
        null=True,
        default=_('unknown'),
        max_length=100,
    )
    construction_completed_date = models.DateField(
        _('construction completed date'), blank=True, null=True
    )
    alert_date = models.DateField(_('alert date'), blank=True, null=True)
    phase = models.CharField(
        _('phase'), blank=True, null=True, max_length=30, choices=PHASE_CHOICES
    )
    status = models.CharField(
        _('status'), blank=True, null=True, max_length=40, choices=STATUS_CHOICES
    )
    external_url = models.URLField(_('external URL'), blank=True, null=True)
    cross_section = models.ImageField(
        _('cross section'), upload_to='photos', blank=True, null=True
    )
    faq = models.ManyToManyField(Question, verbose_name=_('faq'), blank=True)
    photos = GenericRelation(Photo)
    likes = GenericRelation(Like)

    class Meta:
        verbose_name = _('project')
        verbose_name_plural = _('projects')

    def center(self):
        if self.geometry:
            return self.geometry.point_on_surface

    def length(self):
        if self.geometry:
            return self.geometry.transform(self.TRANSFORM_EPSG_3035, clone=True).length

    def __str__(self):
        return self.project_key


class Profile(BaseModel):
    MALE = 'm'
    FEMALE = 'f'
    OTHER = 'o'
    SEX_CHOICES = ((MALE, _('male')), (FEMALE, _('female')), (OTHER, _('other')))
    RACING_CYCLE = 'racing_cycle'
    CITY_BIKE = 'city_bike'
    MOUNTAIN_BIKE = 'mountain_bike'
    E_BIKE = 'e_bike'
    CARGO_BIKE = 'cargo_bike'
    E_CARGO_BIKE = 'e_cargo_bike'
    CATEGORY_OF_BIKE_CHOICES = (
        (RACING_CYCLE, _('racing cycle')),
        (CITY_BIKE, _('city bike')),
        (MOUNTAIN_BIKE, _('mountain bike')),
        (E_BIKE, _('e-bike')),
        (CARGO_BIKE, _('cargo bike')),
        (E_CARGO_BIKE, _('e-cargo-bike')),
    )
    NEVER = 0
    ONCE_PER_MONTH = 1
    ONCE_PER_WEEK = 2
    ONCE_PER_DAY = 3
    USAGE_CHOICES = (
        (NEVER, _('never')),
        (ONCE_PER_DAY, _('once per day')),
        (ONCE_PER_WEEK, _('once per week')),
        (ONCE_PER_MONTH, _('once per month')),
    )
    age = models.PositiveSmallIntegerField(_('age'), blank=True, null=True)
    category_of_bike = models.CharField(
        _('category of bike'),
        blank=True,
        null=True,
        max_length=20,
        choices=CATEGORY_OF_BIKE_CHOICES,
    )
    has_trailer = models.NullBooleanField(_('has trailer'), blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    postal_code = models.CharField(
        _('postal code'), blank=True, null=True, max_length=5
    )
    sex = models.CharField(
        _('sex'), blank=True, null=True, max_length=1, choices=SEX_CHOICES
    )
    speed = models.PositiveSmallIntegerField(_('speed'), blank=True, null=True)
    security = models.PositiveSmallIntegerField(_('security'), blank=True, null=True)
    usage = models.PositiveSmallIntegerField(
        _('usage'), blank=True, null=True, choices=USAGE_CHOICES
    )

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')


class Report(BaseModel):
    STATUS_NEW = 'new'
    STATUS_VERIFICATION = 'verification'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_DONE = 'done'

    STATUS_CHOICES = (
        (STATUS_NEW, _('new')),
        (STATUS_VERIFICATION, _('verification')),
        (STATUS_ACCEPTED, _('accepted')),
        (STATUS_REJECTED, _('rejected')),
        (STATUS_DONE, _('done')),
    )

    SUBJECT_BIKE_STANDS = 'BIKE_STANDS'
    SUBJECT_CHOICES = ((SUBJECT_BIKE_STANDS, _('bike stands')),)

    address = models.TextField(_('address'), blank=True, null=True)
    geometry = models.PointField(_('geometry'), srid=4326)
    subject = models.CharField(_('subject'), max_length=100, choices=SUBJECT_CHOICES)
    description = models.CharField(
        _('description'), blank=True, null=True, max_length=1000
    )
    likes = GenericRelation(Like)
    photo = GenericRelation(Photo)
    published = models.BooleanField(_('published'), default=True)
    status = models.CharField(
        _('status'),
        blank=True,
        null=True,
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
    )
    status_reason = models.TextField(_('reason for status'), blank=True, null=True)
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _('report')
        verbose_name_plural = _('reports')


class BikeStands(Report):
    number = models.PositiveSmallIntegerField(_('number'))
    fee_acceptable = models.BooleanField(_('fee_acceptable'), default=False)

    class Meta:
        verbose_name = _('bike stands')
        verbose_name_plural = _('bike stands')


class PlaystreetSignup(BaseModel):
    campaign = models.CharField(_('campaign'), max_length=64)
    street = models.CharField(_('play_street'), max_length=128)
    first_name = models.TextField(_('first_name'))
    last_name = models.TextField(_('last_name'))
    email = models.CharField(_('email'), max_length=255)
    tos_accepted = models.BooleanField(_('tos_accepted'), default=False)
    captain = models.BooleanField(_('captain'), default=False)
    message = models.TextField(_('message'), blank=True)

    class Meta:
        verbose_name = _('playstreet_signup')
        verbose_name_plural = _('playstreet_signups')
        ordering = ['campaign', 'street']


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
    )

    TIME_WEEKEND = 'weekend'
    TIME_WEEK = 'week'

    TIME_CHOICES = ((TIME_WEEKEND, _('weekend')), (TIME_WEEK, _('whole week')))

    CAMPAIGN_CHOICES = [('xhain', 'Friedrichshain-Kreuzberg 2020')]

    campaign = models.CharField(_('campaign'), choices=CAMPAIGN_CHOICES, max_length=32)
    status = models.CharField(
        _('status'), max_length=64, choices=STATUS_CHOICES, default=STATUS_NEW
    )

    shop_name = models.CharField(_('shop name'), max_length=255)
    first_name = models.CharField(_('first name'), max_length=255)
    last_name = models.CharField(_('last name'), max_length=255)
    category = models.CharField(_('category'), choices=CATEGORY_CHOICES, max_length=255)
    email = models.CharField(_('email'), max_length=255)
    phone = models.CharField(
        _('telephone number'), max_length=32, null=True, blank=True
    )
    usage = models.TextField(_('usage'), null=True, blank=True)

    opening_hours = models.CharField(
        _('opening hours'), max_length=32, choices=TIME_CHOICES
    )
    regulation = models.IntegerField(
        _('regulation'), choices=REGULATION_CHOICES, default=0
    )
    address = models.TextField(_('address'))
    shopfront_length = models.PositiveIntegerField(_('shopfront length'))
    geometry = models.PointField(_('geometry'), srid=4326)

    area = models.GeometryField(
        _('installation area'), srid=4326, null=True, blank=True
    )

    certificate = models.FileField(
        upload_to=get_upload_path, verbose_name=_('registration certificate'), null=True, blank=True
    )

    tos_accepted = models.BooleanField(_('tos_accepted'), default=False)
    agreement_accepted = models.BooleanField(_('agreement accepted'), default=False)

    access_key = models.UUIDField(default=uuid.uuid4, editable=False)

    note = models.TextField(_('note for the registrant'), blank=True)

    class Meta:
        verbose_name = _('gastro_signup')
        verbose_name_plural = _('gastro_signups')
        ordering = ['campaign', 'address']

    def __str__(self):
        if self.shop_name is not None and len(self.shop_name) > 0:
            return self.shop_name
        return f"Schankstraßen-Anmeldung {self.id}"
