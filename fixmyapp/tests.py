from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase
from .models import Edge, Project


class ProjectTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name='Lorem ipsum')
        self.edges = []

        for i in range(3):
            self.edges.append(Edge.objects.create(
                objectid=i,
                gml_id='re_vms_detailnetz_str.9999',
                spatial_name='9999',
                spatial_alias='Mariendorfer Damm',
                spatial_type='LineString',
                elem_nr='45460003_45460015.0' + str(i),
                strschl='02959',
                str_name='Mariendorfer Damm',
                str_bez='B96',
                strklasse1='II',
                strklasse='B',
                strklasse2='STRA',
                vricht='B',
                bezirk='Tempelhof-Schöneberg',
                stadtteil='Mariendorf',
                ebene='0',
                von_vp='45460003',
                bis_vp='45460015',
                laenge=20100101,
                gilt_von=20100101,
                okstra_id='787C5A383D0B434E88FFA2D60EDA90BC',
                geom=MultiLineString()
            ))

    def test_geometry_hash_is_saved(self):
        self.assertIsNone(self.project.geom_hash)
        self.project.edges.add(self.edges[0])
        self.project.save()
        self.assertIsNotNone(self.project.geom_hash)

    def test_has_updated_edges(self):
        for e in self.edges:
            self.project.edges.add(e)

        self.project.save()

        self.assertFalse(self.project.has_updated_edges())

        edge = Edge.objects.get(pk=1)
        edge.str_bez = 'B97'
        edge.save()

        self.assertTrue(self.project.has_updated_edges())
