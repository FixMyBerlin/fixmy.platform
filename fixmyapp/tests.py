from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString, MultiLineString
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from .models import Edge, Planning, PlanningSection, PlanningSectionDetails
import decimal
import json
import tempfile


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
        self.assertAlmostEqual(self.details[0].cycling_infrastructure_sum(), decimal.Decimal('21.90'), 2)
        self.assertAlmostEqual(self.details[1].cycling_infrastructure_sum(), decimal.Decimal('0.00'), 2)
        self.assertAlmostEqual(self.details[2].cycling_infrastructure_sum(), decimal.Decimal('485.95'), 2)

    def test_cycling_infrastructure_ratio(self):
        self.assertAlmostEqual(self.details[0].cycling_infrastructure_ratio(), decimal.Decimal('0.025'), 3)
        self.assertAlmostEqual(self.details[1].cycling_infrastructure_ratio(), decimal.Decimal('0.000'), 3)
        self.assertAlmostEqual(self.details[2].cycling_infrastructure_ratio(), decimal.Decimal('0.982'), 3)

    def test_road_type(self):
        self.assertAlmostEqual(self.details[0].road_type(), decimal.Decimal('0.6'), 1)
        self.assertAlmostEqual(self.details[1].road_type(), decimal.Decimal('0.6'), 1)
        self.assertAlmostEqual(self.details[2].road_type(), decimal.Decimal('1.7'), 1)

    def test_velocity_index(self):
        self.assertAlmostEqual(self.details[0].velocity_index(), decimal.Decimal('1.0'), 1)
        self.assertAlmostEqual(self.details[1].velocity_index(), decimal.Decimal('1.0'), 1)
        self.assertAlmostEqual(self.details[2].velocity_index(), decimal.Decimal('0.7'), 1)

    def test_safety_index(self):
        self.assertAlmostEqual(self.details[0].safety_index(), decimal.Decimal('5.3'), 1)
        self.assertAlmostEqual(self.details[1].safety_index(), decimal.Decimal('5.3'), 1)
        self.assertAlmostEqual(self.details[2].safety_index(), decimal.Decimal('7.7'), 1)

    def test_velocity_index_average(self):
        self.assertAlmostEqual(
            self.planning_sections[0].velocity_index(),
            (self.details[0].velocity_index() + self.details[1].velocity_index()) / 2,
            1
        )
        self.assertAlmostEqual(
            self.planning_sections[1].velocity_index(),
            self.details[2].velocity_index(),
            1
        )

    def test_safety_index_average(self):
        self.assertAlmostEqual(
            self.planning_sections[0].safety_index(),
            (self.details[0].safety_index() + self.details[1].safety_index()) / 2,
            1
        )
        self.assertAlmostEqual(
            self.planning_sections[1].safety_index(),
            self.details[2].safety_index(),
            1
        )


class FeedbackTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_post_feedback(self):
        data = {
            'name': 'Random cyclist',
            'email': 'r.c@example.de',
            'subject': 'Lorem ipsum',
            'message': 'Lorem ipsum dolor sit'
        }
        response = self.client.post(
            '/api/feedback',
            data=json.dumps(data),
            content_type='application/json')

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            'From: {} <{}>'.format(data['name'], data['email']),
            mail.outbox[0].message()._payload
        )
        self.assertIn(
            'Subject: {}'.format(data['subject']),
            mail.outbox[0].message()._payload,
        )
        self.assertIn(
            data['message'],
            mail.outbox[0].message()._payload,
        )


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ReportTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_post_report(self):
        data = {
            'address': 'Potsdamer Platz 1',
            'description': 'Lorem ipsum dolor sit',
            'details': {
                'subject': 'BIKE_STANDS',
                'number': 3,
                'placement': 'SIDEWALK',
                'fee': 0
            },
            'geometry': {
                'type': 'Point',
                'coordinates': [
                    13.34635540636318,
                    52.52565990333657
                ]
            },
            'photo': 'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs='
        }
        response = self.client.post(
            '/api/reports',
            data=json.dumps(data),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('address'), data['address'])
        self.assertEqual(response.json().get('details'), data['details'])
        self.assertEqual(response.json().get('description'), data['description'])
        self.assertEqual(response.json().get('geometry'), data['geometry'])
        self.assertIn('id', response.json())

    def test_get_reports(self):
        response = self.client.get('/api/reports')
        self.assertEqual(response.status_code, 200)


class LikeTest(TestCase):

    def setUp(self):
        get_user_model().objects.create_user('foo', 'foo@example.org', 'bar')
        self.client = Client()
        self.credentials = {'username': 'foo', 'password': 'bar'}
        self.planning = Planning.objects.create(
            title='Lorem ipsum',
            side=Planning.BOTH,
        )
        self.url = reverse('likes', kwargs={'pk': self.planning.id})

    def test_get_like(self):
        response = self.client.get(
            self.url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_get_like_as_anonymous(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_post_like(self):
        response = self.client.post(
            self.url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'user_has_liked': True, 'likes': 1})

        response = self.client.post(
            self.url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def _get_authorization_header(self):
        response = self.client.post(
            '/api/jwt/create/',
            json.dumps(self.credentials),
            content_type='application/json')
        return {'HTTP_AUTHORIZATION': 'JWT ' + response.json()['token']}


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ViewsTest(TestCase):

    fixtures = [
        'edges',
        'planningsections',
        'planningsectiondetails',
        'plannings'
    ]

    def test_planning_section_list(self):
        response = self.client.get('/api/planning-sections')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(response.json().get('count'), 5)

    def test_planning_section_detail(self):
        response = self.client.get('/api/planning-sections/2725')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertIn('plannings', response.json())
        self.assertIn('details', response.json())

    def test_planning_list(self):
        response = self.client.get('/api/plannings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(response.json().get('count'), 3)

    def test_planning_detail(self):
        response = self.client.get('/api/plannings/4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertIn('planning_sections', response.json())


class CommandTestCase(TestCase):
    fixtures = [
        'edges',
        'planningsections',
        'planningsectiondetails',
        'plannings'
    ]

    def test_exportplanningsections(self):
        with tempfile.NamedTemporaryFile() as f:
            call_command('exportplanningsections', f.name)
            export = json.load(f)
            self.assertEqual(export.get('type'), 'FeatureCollection')
            self.assertEqual(type(export.get('features')), list)
            # There are 5 planning sections in the fixtures and for each
            # planning section another feature is added to the export.
            self.assertEqual(len(export.get('features')), 10)
