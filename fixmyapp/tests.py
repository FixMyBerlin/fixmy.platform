from django.contrib.gis.geos import LineString, MultiLineString
from django.test import TestCase
from .models import Edge, PlanningSection, PlanningSectionDetails
import decimal


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
        self.planning_sections = [
            PlanningSection.objects.create(name='Foo'),
            PlanningSection.objects.create(name='Bar'),
        ]
        self.details = [
            PlanningSectionDetails.objects.create(
                planning_section=self.planning_sections[0],
                side=PlanningSectionDetails.RIGHT,
                speed_limit=30,
                daily_traffic=decimal.Decimal(5110.15),
                daily_traffic_heavy=decimal.Decimal(40.98),
                daily_traffic_cargo=decimal.Decimal(521.55),
                daily_traffic_bus=decimal.Decimal(4.85),
                length=decimal.Decimal(874.77),
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
                rva11=decimal.Decimal(21.9),
                rva12=0,
                rva13=0
            ),
            PlanningSectionDetails.objects.create(
                planning_section=self.planning_sections[0],
                side=PlanningSectionDetails.LEFT,
                speed_limit=30,
                daily_traffic=decimal.Decimal(5110.15),
                daily_traffic_heavy=decimal.Decimal(40.98),
                daily_traffic_cargo=decimal.Decimal(521.55),
                daily_traffic_bus=decimal.Decimal(4.85),
                length=decimal.Decimal(874.77),
                crossings=3,
                orientation=PlanningSectionDetails.NORTH,
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
                rva11=0,
                rva12=0,
                rva13=0
            ),
            PlanningSectionDetails.objects.create(
                planning_section=self.planning_sections[1],
                side=PlanningSectionDetails.RIGHT,
                speed_limit=50,
                daily_traffic=decimal.Decimal(8295.0),
                daily_traffic_heavy=decimal.Decimal(532.12),
                daily_traffic_cargo=decimal.Decimal(846.0),
                daily_traffic_bus=decimal.Decimal(129.12),
                length=decimal.Decimal(500.76),
                crossings=1,
                orientation=PlanningSectionDetails.EAST,
                rva1=decimal.Decimal(216.0621912),
                rva2=0,
                rva3=decimal.Decimal(485.9469249),
                rva4=0,
                rva5=0,
                rva6=0,
                rva7=0,
                rva8=0,
                rva9=0,
                rva10=0,
                rva11=0,
                rva12=0,
                rva13=0
            ),
        ]

    def test_cycling_infrastructure_sum(self):
        self.assertAlmostEqual(self.details[0].cycling_infrastructure_sum(), decimal.Decimal(21.9), 4)
        self.assertAlmostEqual(self.details[1].cycling_infrastructure_sum(), 0, 4)
        self.assertAlmostEqual(self.details[2].cycling_infrastructure_sum(), decimal.Decimal(485.946924867869), 4)

    def test_cycling_infrastructure_ratio(self):
        self.assertAlmostEqual(self.details[0].cycling_infrastructure_ratio(), decimal.Decimal(0.0252080527642529), 4)
        self.assertAlmostEqual(self.details[1].cycling_infrastructure_ratio(), decimal.Decimal(0), 4)
        self.assertAlmostEqual(self.details[2].cycling_infrastructure_ratio(), decimal.Decimal(0.982187171290866), 4)

    def test_road_type(self):
        self.assertAlmostEqual(self.details[0].road_type(), decimal.Decimal(0.638769205), 4)
        self.assertAlmostEqual(self.details[1].road_type(), decimal.Decimal(0.638769205), 4)
        self.assertAlmostEqual(self.details[2].road_type(), decimal.Decimal(1.7158333333), 4)

    def test_velocity_index(self):
        self.assertAlmostEqual(self.details[0].velocity_index(), decimal.Decimal(3.47479194723575), 4)
        self.assertAlmostEqual(self.details[1].velocity_index(), decimal.Decimal(3.5), 4)
        self.assertAlmostEqual(self.details[2].velocity_index(), decimal.Decimal(2.5), 4)

    def test_safety_index(self):
        self.assertAlmostEqual(self.details[0].safety_index(), decimal.Decimal(2.861230795), 4)
        self.assertAlmostEqual(self.details[1].safety_index(), decimal.Decimal(2.861230795), 4)
        self.assertAlmostEqual(self.details[2].safety_index(), decimal.Decimal(3.92805555556667), 4)

    def test_velocity_index_average(self):
        self.assertAlmostEqual(
            self.planning_sections[0].velocity_index(),
            (self.details[0].velocity_index() + self.details[1].velocity_index()) / 2,
            4
        )
        self.assertAlmostEqual(
            self.planning_sections[1].velocity_index(),
            self.details[2].velocity_index(),
            4
        )

    def test_safety_index_average(self):
        self.assertAlmostEqual(
            self.planning_sections[0].safety_index(),
            (self.details[0].safety_index() + self.details[1].safety_index()) / 2,
            4
        )
        self.assertAlmostEqual(
            self.planning_sections[1].safety_index(),
            self.details[2].safety_index(),
            4
        )
