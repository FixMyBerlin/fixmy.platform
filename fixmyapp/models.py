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
    description = models.TextField()
    edges = models.ManyToManyField(Edge)
    geom_hash = models.CharField(max_length=40, null=True)

    def has_updated_edges(self):
        return any([e for e in self.edges.all()
             if e.modified_date > self.modified_date])

    def save(self, *args, **kwargs):
        if self.id:
            sha1 = hashlib.sha1()
            for g in self.edges.values_list('geom', flat=True):
                sha1.update(str(g).encode('ascii'))
            self.geom_hash = sha1.hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
