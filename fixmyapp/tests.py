from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase
from .models import Edge, PlanningSection, PlanningSectionDetails


class PlanningSectionTests(TestCase):

    def setUp(self):
        self.planning_section = PlanningSection.objects.create(name='Lorem ipsum')
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
                        (13.3529025205514 + i, 52.4694951051436 + i),
                        (13.3529481208319 + i, 52.4678335717279 + i)
                    )
                )
            ))

    def test_compute_geometry_hash(self):
        self.assertIsNotNone(self.planning_section.compute_geom_hash())
        self.planning_section.edges.add(self.edges[0])
        self.assertIsNotNone(self.planning_section.compute_geom_hash())
        self.assertEqual(len(self.planning_section.compute_geom_hash()), 40)

    def test_adding_edges_is_detected(self):
        self.assertFalse(self.planning_section.has_updated_edges())

        for e in self.edges:
            self.planning_section.edges.add(e)

        self.assertTrue(self.planning_section.has_updated_edges())

    def test_modifying_edges_is_detected(self):
        for e in self.edges:
            self.planning_section.edges.add(e)

        self.planning_section.geom_hash = self.planning_section.compute_geom_hash()
        self.planning_section.save()

        self.assertFalse(self.planning_section.has_updated_edges())

        edge = Edge.objects.all()[0]
        edge.geom = MultiLineString(
            LineString(
                (12.3529025205514, 52.4694951051436),
                (12.3529481208319, 52.4678335717279)
            )
        )
        edge.save()

        self.assertTrue(self.planning_section.has_updated_edges())

    def test_removing_edges_is_detected(self):
        for e in self.edges:
            self.planning_section.edges.add(e)

        self.planning_section.geom_hash = self.planning_section.compute_geom_hash()
        self.planning_section.save()

        self.assertFalse(self.planning_section.has_updated_edges())

        self.planning_section.edges.remove(Edge.objects.all()[0])

        self.assertTrue(self.planning_section.has_updated_edges())

    def test_reordering_edge_geometries_is_ignored(self):
        for e in self.edges:
            self.planning_section.edges.add(e)

        self.planning_section.geom_hash = self.planning_section.compute_geom_hash()
        self.planning_section.save()

        self.assertFalse(self.planning_section.has_updated_edges())

        edge = Edge.objects.all()[0]
        edge.geom = MultiLineString(
            LineString(
                (13.3529481208319, 52.4678335717279),
                (13.3529025205514, 52.4694951051436)
            )
        )
        edge.save()

        self.assertFalse(self.planning_section.has_updated_edges())


class PlanningSectionDetailsTest(TestCase):

    def setUp(self):
        self.planning_section = PlanningSection.objects.create(
            name='Lorem ipsum')
        self.details = PlanningSectionDetails.objects.create(
            planning_section=self.planning_section,
            side=PlanningSectionDetails.RIGHT,
            speed_limit=30,
            daily_traffic=5110.15,
            daily_traffic_heavy=40.98,
            daily_traffic_cargo=521.55,
            daily_traffic_bus=4.85,
            length=874.77,
            crossings=1,
            orientation=PlanningSectionDetails.SOUTH,
            rva1=0,
            rva2=0,
            rva3=0,
            rva4=0,
            rva5=0,
            rva6=0,
            rva7=0,
            rva8=0,
            rva9=0,
            rva10=0,
            rva11=21.9,
            rva12=0,
            rva13=0
        )

    def test_velocity_index(self):
        self.assertEquals(self.details.velocity_index(), 3.47479194723575)

    def test_safety_index(self):
        self.assertEquals(self.details.velocity_index(), 2.861230795)
