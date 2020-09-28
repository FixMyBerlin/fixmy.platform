import csv
import json
import tempfile
import uuid
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.management import call_command
from django.core.exceptions import PermissionDenied
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from fixmyapp.tests import LikeTest
from fixmyapp.models import NoticeSetting
from fixmydjango.utils import get_templates_config
from .models import Report, StatusNotice

# Create your tests here.
@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ApiTests(TestCase):
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

    def test_report_notices(self):
        # Create a report
        report_resp = self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        id = report_resp.json()['id']
        # Assign user to it, creating default notification setting for that user
        self.client.patch(
            '/api/reports/{}'.format(id),
            data=json.dumps({'user': self.user.pk}),
            content_type='application/json',
        )
        # Modify report status
        report = Report.objects.get(pk=id)
        report.status = Report.STATUS_PLANNING
        report.save()

        user_id = report.user.id
        access_key = report.user.notice_settings.first().access_key

        # Test disabling notice with invalid access key
        response = self.client.get(f'/api/reports/unsubscribe/{user_id}/{uuid.uuid4()}')
        self.assertEqual(response.status_code, 403)
        response = self.client.get(f'/api/reports/unsubscribe/{user_id}/<fake_key>')
        self.assertEqual(response.status_code, 403)
        report.refresh_from_db()
        self.assertTrue(report.user.notice_settings.first().send)

        # Test disabling notice from link sent with user notice email
        for template_set in settings.AVAILABLE_TEMPLATE_SETS:
            with self.settings(
                TEMPLATES=get_templates_config(
                    template_set, settings.BASE_DIR, settings.AVAILABLE_TEMPLATE_SETS
                )
            ):
                self.client.get(f'/api/reports/unsubscribe/{user_id}/{access_key}')

        report.refresh_from_db()
        self.assertFalse(report.user.notice_settings.first().send)


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


class UnitTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'foo', 'foo@example.org', 'bar'
        )
        self.report = Report.objects.create(
            address='Potsdamer Platz 1',
            description='Lorem ipsum dolor sit',
            geometry=Point(13.346_355_406_363_18, 52.525_659_903_336_57),
            user=self.user,
        )
        self.planning = Report.objects.create(
            address='Potsdamer Platz 3',
            description='Lorem ipsum dolor sit',
            geometry=Point(13.346_365_406_363_18, 52.525_669_903_336_57),
            status=Report.STATUS_PLANNING,
        )
        self.planning.origin.add(self.report)

    def test_report_notifications(self):
        self.report.status = Report.STATUS_REPORT_ACCEPTED
        self.report.save()

        notification = StatusNotice.objects.get(report=self.report)
        assert notification.status == self.report.status

    def test_planning_notifications(self):
        self.planning.status = Report.STATUS_EXECUTION
        self.planning.save()

        notification = StatusNotice.objects.get(report=self.planning)
        assert notification.user == self.report.user

    def test_planning_notifications_anonymous_origin(self):
        # Test if origin is anonymous
        self.report.user = None
        self.report.save()
        self.planning.status = Report.STATUS_EXECUTION
        self.planning.save()

        assert StatusNotice.objects.filter(report=self.planning).count() == 0

    def test_disabled_notification(self):
        notice_setting, _created = NoticeSetting.objects.get_or_create(
            user=self.user, kind=NoticeSetting.REPORT_UPDATE_KIND
        )
        notice_setting.send = False
        notice_setting.save()

        self.report.status = Report.STATUS_REPORT_ACCEPTED
        self.report.save()

        assert StatusNotice.objects.filter(report=self.report).count() == 0
