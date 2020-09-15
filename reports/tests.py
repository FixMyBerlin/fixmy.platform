import csv
import json
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from fixmyapp.tests import LikeTest
from .models import Report

# Create your tests here.
@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ReportTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'foo', 'foo@example.org', 'bar'
        )
        self.client = Client()
        self.data = {
            'address': 'Potsdamer Platz 1',
            'description': 'Lorem ipsum dolor sit',
            'details': {'subject': 'BIKE_STANDS', 'number': 3, 'fee_acceptable': True},
            'geometry': {
                'type': 'Point',
                'coordinates': [13.346_355_406_363_18, 52.525_659_903_336_57],
            },
            'photo': 'data:image/gif;base64,R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs=',
        }

    def test_post_report(self):
        response = self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
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
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        id = response.json()['id']
        report = Report.objects.get(pk=id)
        self.assertIsNone(report.user)
        response = self.client.patch(
            '/api/reports/{}'.format(id),
            data=json.dumps({'user': self.user.pk}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(pk=id)
        self.assertIsNotNone(report.user)
        self.assertEqual(report.user.pk, self.user.pk)
        response = self.client.patch(
            '/api/reports/{}'.format(id),
            data=json.dumps({'user': self.user.pk}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_export_reports_csv(self):
        self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='csv')
            csv_reader = csv.DictReader(f, dialect='excel')
            self.assertIn('ID', csv_reader.fieldnames)

    def test_export_reports_geojson(self):
        self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='geojson')
            data = json.load(f)
            self.assertIn('id', data["features"][0]["properties"].keys())

    def test_import_reports(self):
        self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f:
            call_command('exportreports', f.name, format='geojson')
            data = json.load(f)

        data["features"][0]["properties"]["address"] = "test"
        data["features"][0]["properties"]["number"] = 1

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f1:
            json.dump(data, f1)
            f1.seek(0)
            call_command('importreports', f1.name)

        reports = Report.objects.all()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0].address, 'test')
        self.assertEqual(reports[0].bikestands.number, 1)

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f2:
            json.dump(data, f2)
            Report.objects.all().delete()
            f2.seek(0)
            call_command('importreports', f2.name)

        reports = Report.objects.all()
        self.assertEqual(len(reports), 1)


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class LikeReportTest(LikeTest, TestCase):
    def setUp(self):
        self.instance = Report.objects.create(
            address='Potsdamer Platz 1',
            description='Lorem ipsum dolor sit',
            geometry=Point(13.346_355_406_363_18, 52.525_659_903_336_57),
        )
        self.instance_url = reverse(
            'reports:report-detail', kwargs={'pk': self.instance.id}
        )
        self.likes_url = reverse(
            'reports:likes-reports', kwargs={'pk': self.instance.id}
        )
        self.liked_by_user_url = reverse('reports:reports-liked-by-user')
        super(LikeReportTest, self).setUp()
