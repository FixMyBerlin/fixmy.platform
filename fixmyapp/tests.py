from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from mailjet_rest.client import Endpoint
from unittest.mock import patch
from .models import (
    Project,
    Report,
    Section,
    SectionDetails
)
import csv
import decimal
import json
import tempfile


class SectionDetailsTest(TestCase):

    def setUp(self):
        self.sections = [
            Section.objects.create(street_name='Foo'),
            Section.objects.create(street_name='Bar'),
        ]
        self.details = [
            SectionDetails.objects.create(
                section=self.sections[0],
                side=SectionDetails.RIGHT,
                speed_limit=30,
                daily_traffic=decimal.Decimal(5110.15),
                daily_traffic_heavy=decimal.Decimal(40.98),
                daily_traffic_cargo=decimal.Decimal(521.55),
                daily_traffic_bus=decimal.Decimal(4.85),
                length=decimal.Decimal(874.77),
                crossings=1,
                orientation=SectionDetails.SOUTH,
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
            SectionDetails.objects.create(
                section=self.sections[0],
                side=SectionDetails.LEFT,
                speed_limit=30,
                daily_traffic=decimal.Decimal(5110.15),
                daily_traffic_heavy=decimal.Decimal(40.98),
                daily_traffic_cargo=decimal.Decimal(521.55),
                daily_traffic_bus=decimal.Decimal(4.85),
                length=decimal.Decimal(874.77),
                crossings=3,
                orientation=SectionDetails.NORTH,
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
            SectionDetails.objects.create(
                section=self.sections[1],
                side=SectionDetails.RIGHT,
                speed_limit=50,
                daily_traffic=decimal.Decimal(8295.0),
                daily_traffic_heavy=decimal.Decimal(532.12),
                daily_traffic_cargo=decimal.Decimal(846.0),
                daily_traffic_bus=decimal.Decimal(129.12),
                length=decimal.Decimal(500.76),
                crossings=1,
                orientation=SectionDetails.EAST,
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
            self.sections[0].velocity_index(),
            (self.details[0].velocity_index() + self.details[1].velocity_index()) / 2,
            1
        )
        self.assertAlmostEqual(
            self.sections[1].velocity_index(),
            self.details[2].velocity_index(),
            1
        )

    def test_safety_index_average(self):
        self.assertAlmostEqual(
            self.sections[0].safety_index(),
            (self.details[0].safety_index() + self.details[1].safety_index()) / 2,
            1
        )
        self.assertAlmostEqual(
            self.sections[1].safety_index(),
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
        self.user = get_user_model().objects.create_user(
            'foo', 'foo@example.org', 'bar')
        self.client = Client()
        self.data = {
            'address': 'Potsdamer Platz 1',
            'description': 'Lorem ipsum dolor sit',
            'details': {
                'subject': 'BIKE_STANDS',
                'number': 3,
                'fee_acceptable': True
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

    def test_post_report(self):
        response = self.client.post(
            '/api/reports',
            data=json.dumps(self.data),
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json().get('address'), self.data['address'])
        self.assertEqual(response.json().get('details'), self.data['details'])
        self.assertEqual(response.json().get('description'), self.data['description'])
        self.assertEqual(response.json().get('geometry'), self.data['geometry'])
        self.assertIn('id', response.json())
        self.assertIn('url', response.json())
        self.assertIn('created_date', response.json())
        self.assertIn('modified_date', response.json())

    def test_get_reports(self):
        response = self.client.get('/api/reports')
        self.assertEqual(response.status_code, 200)

    def test_patch_report(self):
        response = self.client.post(
            '/api/reports',
            data=json.dumps(self.data),
            content_type='application/json')
        id = response.json()['id']
        report = Report.objects.get(pk=id)
        self.assertIsNone(report.user)
        response = self.client.patch(
            '/api/reports/{}'.format(id),
            data=json.dumps({'user': self.user.pk}),
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(pk=id)
        self.assertIsNotNone(report.user)
        self.assertEqual(report.user.pk, self.user.pk)
        response = self.client.patch(
            '/api/reports/{}'.format(id),
            data=json.dumps({'user': self.user.pk}),
            content_type='application/json')
        self.assertEqual(response.status_code, 403)

    def test_export_reports_csv(self):
        self.client.post(
            '/api/reports',
            data=json.dumps(self.data),
            content_type='application/json')
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='csv')
            csv_reader = csv.DictReader(f, dialect='excel')
            self.assertIn('ID', csv_reader.fieldnames)

    def test_export_reports_geojson(self):
        self.client.post(
            '/api/reports',
            data=json.dumps(self.data),
            content_type='application/json')
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='geojson')
            data = json.load(f)
            self.assertIn('id', data["features"][0]["properties"].keys())

class LikeTest(object):

    def setUp(self):
        get_user_model().objects.create_user('foo', 'foo@example.org', 'bar')
        self.client = Client()
        self.credentials = {'username': 'foo', 'password': 'bar'}

    def test_get_like(self):
        response = self.client.get(
            self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_get_like_as_anonymous(self):
        response = self.client.get(self.likes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_post_like(self):
        response = self.client.post(
            self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'user_has_liked': True, 'likes': 1})

        response = self.client.get(
            self.liked_by_user_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('count'), 1)
        self.assertIn('results', response.json())
        self.assertTrue(response.json().get('results')[0].get('url').endswith(self.instance_url))

        response = self.client.post(
            self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def _get_authorization_header(self):
        response = self.client.post(
            '/api/jwt/create/',
            json.dumps(self.credentials),
            content_type='application/json')
        return {'HTTP_AUTHORIZATION': 'JWT ' + response.json()['access']}


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class LikeProjectTest(LikeTest, TestCase):

    def setUp(self):
        self.instance = Project.objects.create(
            title='Lorem ipsum',
            side=Project.BOTH,
        )
        self.instance_url = reverse('project-detail', kwargs={'pk': self.instance.id})
        self.likes_url = reverse('likes-projects', kwargs={'pk': self.instance.id})
        self.liked_by_user_url = reverse('projects-liked-by-user')
        super(LikeProjectTest, self).setUp()


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class LikeReportTest(LikeTest, TestCase):

    def setUp(self):
        self.instance = Report.objects.create(
            address='Potsdamer Platz 1',
            description='Lorem ipsum dolor sit',
            geometry=Point(13.34635540636318, 52.52565990333657)
        )
        self.instance_url = reverse('report-detail', kwargs={'pk': self.instance.id})
        self.likes_url = reverse('likes-reports', kwargs={'pk': self.instance.id})
        self.liked_by_user_url = reverse('reports-liked-by-user')
        super(LikeReportTest, self).setUp()


@override_settings(TOGGLE_NEWSLETTER=True)
class NewsletterSignupTest(TestCase):

    def setUp(self):
        get_user_model().objects.create_user('foo', 'foo@example.org', 'bar')
        self.client = Client()
        self.credentials = {'username': 'foo', 'password': 'bar'}
        self.url = '/api/newsletter-signup'

    def test_authorization_required(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)

    @patch('requests.Response')
    @patch.object(Endpoint, 'create')
    def test_response_no_content(self, mock_response_class, mock_create):
        mock_response = mock_response_class.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_create.return_value = mock_response
        response = self.client.post(
            self.url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 204)

    def _get_authorization_header(self):
        response = self.client.post(
            '/api/jwt/create/',
            json.dumps(self.credentials),
            content_type='application/json')
        return {'HTTP_AUTHORIZATION': 'JWT ' + response.json()['access']}


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ViewsTest(TestCase):

    fixtures = [
        'projects',
        'sections',
        'sectiondetails',
    ]

    def test_project_list(self):
        response = self.client.get('/api/projects')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(response.json().get('count'), 3)

    def test_project_detail(self):
        response = self.client.get('/api/projects/4')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertIn('geometry', response.json())

    def test_section_list(self):
        response = self.client.get('/api/sections')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(response.json().get('count'), 5)

    def test_section_detail(self):
        response = self.client.get('/api/sections/2725')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertIn('geometry', response.json())
        self.assertIn('details', response.json())


class CommandTestCase(TestCase):
    fixtures = [
        'sections',
        'sectiondetails'
    ]

    def test_exportsections(self):
        with tempfile.NamedTemporaryFile() as f:
            call_command('exportsections', f.name)
            export = json.load(f)
            self.assertEqual(export.get('type'), 'FeatureCollection')
            self.assertEqual(type(export.get('features')), list)
            self.assertEqual(len(export.get('features')), 5)