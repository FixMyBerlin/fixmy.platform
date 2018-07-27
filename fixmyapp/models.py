from django.contrib.gis.db import models
from markdownx.models import MarkdownxField
import hashlib
import random
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
    description = MarkdownxField(blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    edges = models.ManyToManyField(Edge)
    geom_hash = models.CharField(max_length=40, null=True)

    def velocity_index(self, side):
        return round(random.randint(5, 35) * 0.1, 1)

    def safety_index(self, side):
        return round(random.randint(5, 45) * 0.1, 1)

    def has_updated_edges(self):
        return self.geom_hash != self.compute_geom_hash()

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


class Question(BaseModel):
    text = models.CharField(max_length=256)
    answer = MarkdownxField()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('text',)


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
    orientation =  models.CharField(max_length=1, choices=ORIENTATION_CHOICES)
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

    class Meta:
        verbose_name = 'Planning section details'
        verbose_name_plural = 'Planning section details'


class CyclingInfrastructurePhoto(BaseModel):
    planning_section_detail = models.ForeignKey(
        PlanningSectionDetails, related_name='photos', on_delete=models.CASCADE
    )
    src = models.ImageField(verbose_name='Photo')


class Planning(BaseModel):
    CATEGORY_NEW_INFRASTRUCTURE = 'new cycling infrastructure'
    CATEGORY_RENOVATION = 'renovation of cycling infrastructure'
    CATEGORY_BIKE_STREET = 'bike street'
    CATEGORY_MODIFICATION_OF_JUNCTION = 'modification of junction'
    CATEGORY_BIKE_PARKING = 'bike parking'
    CATEGORY_CROSSING_AID = 'crossing aid'
    CATEGORY_MODIFICATION_OF_CROSS_SECTION = 'modification of cross section'
    CATEGORY_MISCELLANEOUS = 'miscellaneous'

    CATEGORY_CHOICES = (
       (CATEGORY_NEW_INFRASTRUCTURE, 'new cycling infrastructure'),
       (CATEGORY_RENOVATION, 'renovation of cycling infrastructure'),
       (CATEGORY_BIKE_STREET, 'bike street'),
       (CATEGORY_MODIFICATION_OF_JUNCTION, 'modification of junction'),
       (CATEGORY_BIKE_PARKING, 'bike parking'),
       (CATEGORY_CROSSING_AID, 'crossing aid'),
       (CATEGORY_MODIFICATION_OF_CROSS_SECTION, 'modification of cross section'),
       (CATEGORY_MISCELLANEOUS, 'miscellaneous'),
    )

    PHASE_DRAFT = 'draft'
    PHASE_PLANNING = 'planning'
    PHASE_REVIEW = 'review'
    PHASE_EXAMINATION = 'examination'
    PHASE_EXECUTION = 'execution'
    PHASE_READY = 'ready'
    PHASE_MISCELLANEOUS = 'miscellaneous'

    PHASE_CHOICES = (
        (PHASE_DRAFT, 'draft'),
        (PHASE_PLANNING, 'planning'),
        (PHASE_REVIEW, 'review'),
        (PHASE_EXAMINATION, 'examination'),
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
    SIDE_CHOICES = (
        (RIGHT, 'right'),
        (LEFT, 'left'),
    )

    planning_sections = models.ManyToManyField(
        PlanningSection, related_name='plannings')
    published = models.BooleanField(default=True)
    title = models.CharField(max_length=256)
    side = models.PositiveSmallIntegerField(blank=True, null=True, choices=SIDE_CHOICES)
    description = MarkdownxField()
    short_description = models.CharField(max_length=200)
    category = models.CharField(blank=True, null=True, max_length=30, choices=CATEGORY_CHOICES)
    project_key = models.CharField(blank=True, null=True, max_length=100)
    costs = models.PositiveIntegerField(blank=True, null=True)
    draft = models.CharField(blank=True, null=True, max_length=100)
    start_of_construction = models.CharField(blank=True, null=True, max_length=100)
    completion = models.CharField(blank=True, null=True, max_length=100)
    phase = models.CharField(blank=True, null=True, max_length=30, choices=PHASE_CHOICES)
    status = models.CharField(blank=True, null=True, max_length=30, choices=STATUS_CHOICES)
    responsible = models.CharField(max_length=256)
    external_url = models.URLField(blank=True, null=True)
    cross_section_photo = models.ImageField(upload_to='photos', blank=True, null=True)
    faq = models.ManyToManyField(Question, blank=True)

    def geometry(self):
        result = self.planning_sections.aggregate(models.Union('edges__geom'))
        return result['edges__geom__union'].merged


class PlanningPhoto(BaseModel):
    planning = models.ForeignKey(
        Planning, related_name='photos', on_delete=models.CASCADE
    )
    height = models.PositiveSmallIntegerField()
    width = models.PositiveSmallIntegerField()
    src = models.ImageField(
        upload_to='photos',
        verbose_name='Image',
        height_field='height',
        width_field='width')


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
