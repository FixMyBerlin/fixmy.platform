from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase
from .models import Edge, Project


class ProjectTests(TestCase):

    def setUp(self):
        self.project = Project.objects.create(name='Lorem ipsum')
        self.edges = []

        for i in range(3):
            self.edges.append(Edge.objects.create(
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
                geom=MultiLineString(
                    LineString(
                        (13.3529025205514, 52.4694951051436),
                        (13.3529481208319, 52.4678335717279)
                    )
                )
            ))

    def test_compute_geometry_hash(self):
        self.assertIsNotNone(self.project.compute_geom_hash())
        self.project.edges.add(self.edges[0])
        self.assertIsNotNone(self.project.compute_geom_hash())
        self.assertEqual(len(self.project.compute_geom_hash()), 40)

    def test_adding_edges_is_detected(self):
        self.assertFalse(self.project.has_updated_edges())

        for e in self.edges:
            self.project.edges.add(e)

        self.assertTrue(self.project.has_updated_edges())

    def test_modifying_edges_is_detected(self):

        for e in self.edges:
            self.project.edges.add(e)

        self.project.geom_hash = self.project.compute_geom_hash()
        self.project.save()

        self.assertFalse(self.project.has_updated_edges())

        edge = Edge.objects.all()[0]
        edge.geom = MultiLineString(
            LineString(
                (12.3529025205514, 52.4694951051436),
                (12.3529481208319, 52.4678335717279)
            )
        )
        edge.save()

        self.project.refresh_from_db()
        self.assertTrue(self.project.has_updated_edges())

    def test_removing_edges_is_detected(self):

        for e in self.edges:
            self.project.edges.add(e)

        self.project.geom_hash = self.project.compute_geom_hash()
        self.project.save()

        self.assertFalse(self.project.has_updated_edges())

        self.project.edges.remove(Edge.objects.all()[0])

        self.assertTrue(self.project.has_updated_edges())
