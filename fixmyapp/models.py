from django.contrib.gis.db import models

class Edge(models.Model):
    objectid = models.IntegerField(primary_key=True)
    gml_parent_id = models.CharField(max_length=255)
    gml_id = models.CharField(max_length=255)
    spatial_geometry = models.CharField(max_length=255)
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


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    edges = models.ManyToManyField(Edge)

    def __str__(self):
        return self.name
