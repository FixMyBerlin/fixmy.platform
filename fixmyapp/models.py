from django.contrib.gis.db import models
import hashlib


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Edge(BaseModel):
    objectid = models.IntegerField(primary_key=True)
    gml_parent_id = models.CharField(max_length=255, blank=True)
    gml_id = models.CharField(max_length=255)
    spatial_geometry = models.CharField(max_length=255, blank=True)
    spatial_name = models.CharField(max_length=255)
    spatial_alias = models.CharField(max_length=255)
    spatial_type = models.CharField(max_length=255)
    elem_nr = models.CharField(max_length=255, unique=True)
    strschl = models.CharField(max_length=255)
    str_name = models.CharField(max_length=255)
    str_bez = models.CharField(max_length=255)
    strklasse1 = models.CharField(max_length=255)
    strklasse = models.CharField(max_length=255)
    strklasse2 = models.CharField(max_length=255)
    vricht = models.CharField(max_length=255)
    bezirk = models.CharField(max_length=255)
    stadtteil = models.CharField(max_length=255)
    ebene = models.CharField(max_length=255)
    von_vp = models.CharField(max_length=255)
    bis_vp = models.CharField(max_length=255)
    laenge = models.FloatField()
    gilt_von = models.IntegerField()
    okstra_id = models.CharField(max_length=255)
    geom = models.MultiLineStringField()

    def __str__(self):
        return self.elem_nr


class Project(BaseModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    edges = models.ManyToManyField(Edge)
    geom_hash = models.CharField(max_length=40, null=True)

    def has_updated_edges(self):
        return self.geom_hash != self.compute_geom_hash()

    def compute_geom_hash(self):
        sha1 = hashlib.sha1()
        if self.id:
            geoms = self.edges.values_list('geom', flat=True)
            for geom_str in sorted(str(g.sort()) for g in geoms):
                sha1.update(geom_str.encode('ascii'))
        return sha1.hexdigest()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.geom_hash = self.compute_geom_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
