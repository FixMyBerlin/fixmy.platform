from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import (
    GenericForeignKey, GenericRelation)
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from markdownx.models import MarkdownxField
import decimal
import hashlib
import uuid


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Edge(models.Model):
    elem_nr = models.CharField(max_length=254, primary_key=True)
    strschl = models.CharField(max_length=254)
    str_name = models.CharField(max_length=254)
    str_bez = models.CharField(max_length=254)
    strklasse1 = models.CharField(max_length=254)
    strklasse = models.CharField(max_length=254)
    strklasse2 = models.CharField(max_length=254)
    vricht = models.CharField(max_length=254)
    bezirk = models.CharField(max_length=254)
    stadtteil = models.CharField(max_length=254)
    ebene = models.FloatField()
    von_vp = models.CharField(max_length=254)
    bis_vp = models.CharField(max_length=254)
    laenge = models.FloatField()
    gilt_von = models.FloatField()
    okstra_id = models.CharField(max_length=254)
    geom = models.MultiLineStringField(srid=4326)

    def __str__(self):
        return self.str_name + " (Elem Nr: " + self.elem_nr + ")"


class PlanningSection(BaseModel):
    name = models.CharField(max_length=100)
    suffix = models.CharField(blank=True, null=True, max_length=3)
    street_category = models.PositiveSmallIntegerField(null=True)
    edges = models.ManyToManyField(Edge)
    geom_hash = models.CharField(max_length=40, null=True)

    def borough(self):
        return self.edges.first().bezirk

    def geometry(self):
        result = self.edges.aggregate(models.Union('geom'))
        return result['geom__union'].merged

    def velocity_index(self):
        if len(self.details.all()) > 0:
            return sum(d.velocity_index() for d in self.details.all()) / len(self.details.all())
        else:
            return 0

    def safety_index(self):
        if len(self.details.all()) > 0:
            return sum(d.safety_index() for d in self.details.all()) / len(self.details.all())
        else:
            return 0

    def has_updated_edges(self):
        return self.geom_hash != self.compute_geom_hash()

    def has_plannings(self):
        return self.planning_set.filter(published=1).count() > 0

    def plannings(self):
        return self.planning_set.filter(published=1)

    def compute_geom_hash(self):
        sha1 = hashlib.sha1()
        if self.id:
            geoms = self.edges.values_list('geom', flat=True)
            points = set(p for ml in geoms for l in ml for p in l)
            for point in sorted(points):
                sha1.update(str(point).encode('ascii'))
        return sha1.hexdigest()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.geom_hash = self.compute_geom_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return '{} ({})'.format(self.name, self.id)


class Section(BaseModel):
    street_name = models.CharField(max_length=100)
    suffix = models.CharField(blank=True, null=True, max_length=3)
    borough = models.CharField(blank=True, null=True, max_length=255)
    street_category = models.PositiveSmallIntegerField(null=True)
    geometry = models.MultiLineStringField(srid=4326, null=True)

    def velocity_index(self):
        if len(self.details.all()) > 0:
            return sum(d.velocity_index() for d in self.details.all()) / len(self.details.all())
        else:
            return 0

    def safety_index(self):
        if len(self.details.all()) > 0:
            return sum(d.safety_index() for d in self.details.all()) / len(self.details.all())
        else:
            return 0

    def __str__(self):
        return '{} ({})'.format(self.street_name, self.id)


class Question(BaseModel):
    text = models.CharField(max_length=256)
    answer = MarkdownxField()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('text',)


class Photo(BaseModel):
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    copyright = models.CharField(blank=True, null=True, max_length=256)
    object_id = models.PositiveIntegerField()
    src = models.ImageField(upload_to='photos', verbose_name='File')

    def __str__(self):
        return self.src.name.split('/')[-1]


class Like(BaseModel):
    content_object = GenericForeignKey('content_type', 'object_id')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)


class PlanningSectionDetails(BaseModel):
    RIGHT = 0
    LEFT = 1
    SIDE_CHOICES = (
        (RIGHT, 'right'),
        (LEFT, 'left'),
    )
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
    ORIENTATION_CHOICES = (
        (NORTH, 'north'),
        (EAST, 'east'),
        (SOUTH, 'south'),
        (WEST, 'west'),
    )
    AVG_WIDTH_CROSSINGS = 6
    CI_RATIO_MIN = 0.65

    planning_section = models.ForeignKey(
        PlanningSection, related_name='details', on_delete=models.CASCADE)
    side = models.PositiveSmallIntegerField(choices=SIDE_CHOICES)
    speed_limit = models.PositiveSmallIntegerField()
    daily_traffic = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_heavy = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_cargo = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_bus = models.DecimalField(max_digits=8, decimal_places=2)
    length = models.DecimalField(max_digits=8, decimal_places=2)
    crossings = models.PositiveSmallIntegerField()
    orientation = models.CharField(max_length=1, choices=ORIENTATION_CHOICES)
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
        verbose_name = 'Planning section details'
        verbose_name_plural = 'Planning section details'

    def happy_bike_index(self):
        return self.velocity_index() + self.safety_index()

    def velocity_index(self):
        weighted_sum = sum([
            self.rva3 * 2,
            self.rva4 * 1,
            self.rva7 * 2,
            self.rva8 * 3,
            self.rva9 * 3,
            self.rva10 * 3,
            self.rva11 * 2,
            self.rva12 * 3,
            self.rva13 * 2
        ])

        if self.cycling_infrastructure_sum() > 0:
            ci_factor = weighted_sum / (self.cycling_infrastructure_sum() * 3)
        else:
            ci_factor = decimal.Decimal(weighted_sum / 3)

        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            return (
                self.cycling_infrastructure_ratio() * ci_factor +
                (1 - self.cycling_infrastructure_ratio())
            )
        else:
            return ci_factor

    def safety_index(self):
        offset = decimal.Decimal(3)
        ci_safety = self.cycling_infrastructure_safety()

        if ci_safety <= self.road_type():
            return (offset + ci_safety - self.road_type()) * decimal.Decimal('2.25')
        else:
            return (offset + (ci_safety - self.road_type()) / 3) * decimal.Decimal('2.25')

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
        return sum([
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
            self.rva13
        ])

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
        weighted_sum = sum([
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
            self.rva13 * 1
        ])
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
        return '{} {}'.format(self.planning_section, self.SIDE_CHOICES[self.side][1])


class SectionDetails(BaseModel):
    RIGHT = 0
    LEFT = 1
    SIDE_CHOICES = (
        (RIGHT, 'right'),
        (LEFT, 'left'),
    )
    NORTH = 'N'
    EAST = 'E'
    SOUTH = 'S'
    WEST = 'W'
    ORIENTATION_CHOICES = (
        (NORTH, 'north'),
        (EAST, 'east'),
        (SOUTH, 'south'),
        (WEST, 'west'),
    )
    AVG_WIDTH_CROSSINGS = 6
    CI_RATIO_MIN = 0.65

    section = models.ForeignKey(
        Section, related_name='details', on_delete=models.CASCADE)
    side = models.PositiveSmallIntegerField(choices=SIDE_CHOICES)
    speed_limit = models.PositiveSmallIntegerField()
    daily_traffic = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_heavy = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_cargo = models.DecimalField(max_digits=8, decimal_places=2)
    daily_traffic_bus = models.DecimalField(max_digits=8, decimal_places=2)
    length = models.DecimalField(max_digits=8, decimal_places=2)
    crossings = models.PositiveSmallIntegerField()
    orientation = models.CharField(max_length=1, choices=ORIENTATION_CHOICES)
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
        verbose_name = 'Section details'
        verbose_name_plural = 'Section details'

    def happy_bike_index(self):
        return self.velocity_index() + self.safety_index()

    def velocity_index(self):
        weighted_sum = sum([
            self.rva3 * 2,
            self.rva4 * 1,
            self.rva7 * 2,
            self.rva8 * 3,
            self.rva9 * 3,
            self.rva10 * 3,
            self.rva11 * 2,
            self.rva12 * 3,
            self.rva13 * 2
        ])

        if self.cycling_infrastructure_sum() > 0:
            ci_factor = weighted_sum / (self.cycling_infrastructure_sum() * 3)
        else:
            ci_factor = decimal.Decimal(weighted_sum / 3)

        if self.cycling_infrastructure_ratio() < self.CI_RATIO_MIN:
            return (
                    self.cycling_infrastructure_ratio() * ci_factor +
                    (1 - self.cycling_infrastructure_ratio())
            )
        else:
            return ci_factor

    def safety_index(self):
        offset = decimal.Decimal(3)
        ci_safety = self.cycling_infrastructure_safety()

        if ci_safety <= self.road_type():
            return (offset + ci_safety - self.road_type()) * decimal.Decimal('2.25')
        else:
            return (offset + (ci_safety - self.road_type()) / 3) * decimal.Decimal('2.25')

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
        return sum([
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
            self.rva13
        ])

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
        weighted_sum = sum([
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
            self.rva13 * 1
        ])
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


class Planning(BaseModel):
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
       (CATEGORY_NEW_INFRASTRUCTURE, 'new cycling infrastructure'),
       (CATEGORY_RENOVATION, 'renovation of cycling infrastructure'),
       (CATEGORY_BIKE_STREET, 'bike street'),
       (CATEGORY_MODIFICATION_OF_JUNCTION, 'modification of junction'),
       (CATEGORY_BIKE_PARKING, 'bike parking'),
       (CATEGORY_CROSSING_AID, 'crossing aid'),
       (CATEGORY_MODIFICATION_OF_CROSS_SECTION, 'modification of cross section'),
       (CATEGORY_NEW_STREET, 'new street'),
       (CATEGORY_SHARED_SPACE, 'shared space'),
       (CATEGORY_MISCELLANEOUS, 'miscellaneous'),
    )

    PHASE_DRAFT = 'draft'
    PHASE_PLANNING = 'planning'
    PHASE_REVIEW = 'review'
    PHASE_INACTIVE = 'inactive'
    PHASE_EXECUTION = 'execution'
    PHASE_READY = 'ready'
    PHASE_MISCELLANEOUS = 'miscellaneous'

    PHASE_CHOICES = (
        (PHASE_DRAFT, 'draft'),
        (PHASE_PLANNING, 'planning'),
        (PHASE_REVIEW, 'review'),
        (PHASE_INACTIVE, 'inactive'),
        (PHASE_EXECUTION, 'execution'),
        (PHASE_READY, 'ready'),
        (PHASE_MISCELLANEOUS, 'miscellaneous'),
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
        (STATUS_UNKNOWN, 'unknown'),
        (STATUS_IDEA, 'idea'),
        (STATUS_PRELIMINARY_PLANNING, 'preliminary planning'),
        (STATUS_BLUEPRINT_PLANNING, 'blueprint planning'),
        (STATUS_APPROVAL_PLANNING, 'approval planning'),
        (STATUS_EXAMINATION, 'examination'),
        (STATUS_EXECUTION_PLANNING, 'execution planning'),
        (STATUS_PREPARATION_OF_AWARDING, 'preparation of awarding'),
        (STATUS_AWARDING, 'awarding'),
        (STATUS_APPLICATION_FOR_CONSTRUCTION_SITE, 'application for construction site'),
        (STATUS_EXECUTION_OF_CONSTRUCTION_WORK, 'execution of construction work'),
        (STATUS_READY, 'ready'),
        (STATUS_REVIEW, 'review'),
        (STATUS_CANCELLED, 'cancelled'),
    )

    RIGHT = 0
    LEFT = 1
    BOTH = 2
    SIDE_CHOICES = (
        (RIGHT, 'right'),
        (LEFT, 'left'),
        (BOTH, 'both')
    )

    planning_sections = models.ManyToManyField(PlanningSection)
    published = models.BooleanField(default=True)
    title = models.CharField(max_length=256)
    side = models.PositiveSmallIntegerField(choices=SIDE_CHOICES)
    description = MarkdownxField()
    short_description = models.CharField(blank=True, null=True, max_length=200)
    category = models.CharField(blank=True, null=True, max_length=40, choices=CATEGORY_CHOICES)
    project_key = models.CharField(blank=True, null=True, max_length=100)
    costs = models.PositiveIntegerField(blank=True, null=True)
    draft_submitted = models.CharField(blank=True, null=True, max_length=100)
    construction_started = models.CharField(blank=True, null=True, max_length=100)
    construction_completed = models.CharField(blank=True, null=True, max_length=100)
    phase = models.CharField(blank=True, null=True, max_length=30, choices=PHASE_CHOICES)
    status = models.CharField(blank=True, null=True, max_length=40, choices=STATUS_CHOICES)
    responsible = models.CharField(max_length=256)
    external_url = models.URLField(blank=True, null=True)
    cross_section_photo = models.ImageField(upload_to='photos', blank=True, null=True)
    faq = models.ManyToManyField(Question, blank=True)
    photos = GenericRelation(Photo)
    likes = GenericRelation(Like)

    def geometry(self):
        result = self.planning_sections.aggregate(models.Union('edges__geom'))
        return result['edges__geom__union'].merged

    def center(self):
        return self.geometry().point_on_surface


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
        (CATEGORY_NEW_INFRASTRUCTURE, 'new cycling infrastructure'),
        (CATEGORY_RENOVATION, 'renovation of cycling infrastructure'),
        (CATEGORY_BIKE_STREET, 'bike street'),
        (CATEGORY_MODIFICATION_OF_JUNCTION, 'modification of junction'),
        (CATEGORY_BIKE_PARKING, 'bike parking'),
        (CATEGORY_CROSSING_AID, 'crossing aid'),
        (CATEGORY_MODIFICATION_OF_CROSS_SECTION, 'modification of cross section'),
        (CATEGORY_NEW_STREET, 'new street'),
        (CATEGORY_SHARED_SPACE, 'shared space'),
        (CATEGORY_MISCELLANEOUS, 'miscellaneous'),
    )

    PHASE_DRAFT = 'draft'
    PHASE_PLANNING = 'planning'
    PHASE_REVIEW = 'review'
    PHASE_INACTIVE = 'inactive'
    PHASE_EXECUTION = 'execution'
    PHASE_READY = 'ready'
    PHASE_MISCELLANEOUS = 'miscellaneous'

    PHASE_CHOICES = (
        (PHASE_DRAFT, 'draft'),
        (PHASE_PLANNING, 'planning'),
        (PHASE_REVIEW, 'review'),
        (PHASE_INACTIVE, 'inactive'),
        (PHASE_EXECUTION, 'execution'),
        (PHASE_READY, 'ready'),
        (PHASE_MISCELLANEOUS, 'miscellaneous'),
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
        (STATUS_UNKNOWN, 'unknown'),
        (STATUS_IDEA, 'idea'),
        (STATUS_PRELIMINARY_PLANNING, 'preliminary planning'),
        (STATUS_BLUEPRINT_PLANNING, 'blueprint planning'),
        (STATUS_APPROVAL_PLANNING, 'approval planning'),
        (STATUS_EXAMINATION, 'examination'),
        (STATUS_EXECUTION_PLANNING, 'execution planning'),
        (STATUS_PREPARATION_OF_AWARDING, 'preparation of awarding'),
        (STATUS_AWARDING, 'awarding'),
        (STATUS_APPLICATION_FOR_CONSTRUCTION_SITE, 'application for construction site'),
        (STATUS_EXECUTION_OF_CONSTRUCTION_WORK, 'execution of construction work'),
        (STATUS_READY, 'ready'),
        (STATUS_REVIEW, 'review'),
        (STATUS_CANCELLED, 'cancelled'),
    )

    RIGHT = 0
    LEFT = 1
    BOTH = 2
    SIDE_CHOICES = (
        (RIGHT, 'right'),
        (LEFT, 'left'),
        (BOTH, 'both')
    )

    published = models.BooleanField(default=True)
    title = models.CharField(max_length=256)
    side = models.PositiveSmallIntegerField(choices=SIDE_CHOICES)
    responsible = models.CharField(max_length=256)
    description = MarkdownxField()
    short_description = models.CharField(blank=True, null=True, max_length=200)
    geometry = models.GeometryField(blank=True, null=True)
    category = models.CharField(blank=True, null=True, max_length=40, choices=CATEGORY_CHOICES)
    project_key = models.CharField(blank=True, null=True, max_length=100)
    street_name = models.CharField(max_length=100)
    borough = models.CharField(blank=True, null=True, max_length=255)
    costs = models.PositiveIntegerField(blank=True, null=True)
    draft_submitted = models.CharField(blank=True, null=True, max_length=100)
    construction_started = models.CharField(blank=True, null=True, max_length=100)
    construction_completed = models.CharField(blank=True, null=True, max_length=100)
    phase = models.CharField(blank=True, null=True, max_length=30, choices=PHASE_CHOICES)
    status = models.CharField(blank=True, null=True, max_length=40, choices=STATUS_CHOICES)
    external_url = models.URLField(blank=True, null=True)
    cross_section = models.ImageField(upload_to='photos', blank=True, null=True)
    faq = models.ManyToManyField(Question, blank=True)
    photos = GenericRelation(Photo)
    likes = GenericRelation(Like)

    def center(self):
        if self.geometry:
            return self.geometry.point_on_surface


class Profile(BaseModel):
    MALE = 'm'
    FEMALE = 'f'
    OTHER = 'o'
    SEX_CHOICES = (
        (MALE, 'male'),
        (FEMALE, 'female'),
        (OTHER, 'other'),
    )
    RACING_CYCLE = 'racing_cycle'
    CITY_BIKE = 'city_bike'
    MOUNTAIN_BIKE = 'mountain_bike'
    E_BIKE = 'e_bike'
    CARGO_BIKE = 'cargo_bike'
    E_CARGO_BIKE = 'e_cargo_bike'
    CATEGORY_OF_BIKE_CHOICES = (
        (RACING_CYCLE, 'racing cycle'),
        (CITY_BIKE, 'city bike'),
        (MOUNTAIN_BIKE, 'mountain bike'),
        (E_BIKE, 'e-bike'),
        (CARGO_BIKE, 'cargo bike'),
        (E_CARGO_BIKE, 'e-cargo-bike'),
    )
    NEVER = 0
    ONCE_PER_MONTH = 1
    ONCE_PER_WEEK = 2
    ONCE_PER_DAY = 3
    USAGE_CHOICES = (
        (NEVER, 'never'),
        (ONCE_PER_DAY, 'once per day'),
        (ONCE_PER_WEEK, 'once per week'),
        (ONCE_PER_MONTH, 'once per month'),
    )
    age = models.PositiveSmallIntegerField(blank=True, null=True)
    category_of_bike = models.CharField(
        blank=True, null=True, max_length=20, choices=CATEGORY_OF_BIKE_CHOICES)
    has_trailer = models.NullBooleanField(blank=True, null=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    postal_code = models.CharField(blank=True, null=True, max_length=5)
    sex = models.CharField(
        blank=True, null=True, max_length=1, choices=SEX_CHOICES)
    speed = models.PositiveSmallIntegerField(blank=True, null=True)
    security = models.PositiveSmallIntegerField(blank=True, null=True)
    usage = models.PositiveSmallIntegerField(
        blank=True, null=True, choices=USAGE_CHOICES)


class Report(BaseModel):
    STATUS_NEW = 'new'
    STATUS_VERIFICATION = 'verification'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_DONE = 'done'

    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_VERIFICATION, 'verification'),
        (STATUS_ACCEPTED, 'accepted'),
        (STATUS_REJECTED, 'rejected'),
        (STATUS_DONE, 'done')
    )

    address = models.TextField(blank=True, null=True)
    geometry = models.PointField(srid=4326)
    description = models.CharField(blank=True, null=True, max_length=400)
    details = JSONField()
    likes = GenericRelation(Like)
    photo = GenericRelation(Photo)
    published = models.BooleanField(default=True)
    status = models.CharField(
        blank=True,
        null=True,
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW)
    status_reason = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        get_user_model(), blank=True, null=True, on_delete=models.SET_NULL)
