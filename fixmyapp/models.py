from django.contrib.gis.db import models
import hashlib


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
    geom = models.MultiLineStringField(srid=25833)

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
            for g in geoms:
                g.sort()
            for geom_str in sorted(str(g) for g in geoms):
                sha1.update(geom_str.encode('ascii'))
        return sha1.hexdigest()

    def save(self, *args, **kwargs):
        if self.id is None:
            self.geom_hash = self.compute_geom_hash()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
