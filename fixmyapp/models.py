from django.contrib.gis.db import models
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
    description = models.TextField(blank=True)
    progress = models.PositiveSmallIntegerField(default=0)
    edges = models.ManyToManyField(Edge)
    geom_hash = models.CharField(max_length=40, null=True)

    def velocity_index(self, side):
        return round(random.randint(5, 35) * 0.1, 1)

    def security_index(self, side):
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
        return self.name


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
