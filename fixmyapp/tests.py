import csv
import decimal
import json
import tempfile
from anymail.exceptions import AnymailInvalidAddress
from datetime import datetime, timezone, timedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mailjet_rest.client import Endpoint
from unittest.mock import patch
from .models import Project, Report, Section, SectionDetails, GastroSignup


class FailingMockEmailBackend(BaseEmailBackend):
    # This mock email backend raises an AnyMail error on any attempt to
    # send an email

    def send_messages(self, email_messages):
        raise AnymailInvalidAddress(email_message=email_messages[0])


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
                rva13=0,
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
                rva13=0,
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
                rva1=decimal.Decimal(216.062_191_2),
                rva2=0,
                rva3=decimal.Decimal(485.946_924_9),
                rva4=0,
                rva5=0,
                rva6=0,
                rva7=0,
                rva8=0,
                rva9=0,
                rva10=0,
                rva11=0,
                rva12=0,
                rva13=0,
            ),
        ]

    def test_cycling_infrastructure_sum(self):
        self.assertAlmostEqual(
            self.details[0].cycling_infrastructure_sum(), decimal.Decimal('21.90'), 2
        )
        self.assertAlmostEqual(
            self.details[1].cycling_infrastructure_sum(), decimal.Decimal('0.00'), 2
        )
        self.assertAlmostEqual(
            self.details[2].cycling_infrastructure_sum(), decimal.Decimal('485.95'), 2
        )

    def test_cycling_infrastructure_ratio(self):
        self.assertAlmostEqual(
            self.details[0].cycling_infrastructure_ratio(), decimal.Decimal('0.025'), 3
        )
        self.assertAlmostEqual(
            self.details[1].cycling_infrastructure_ratio(), decimal.Decimal('0.000'), 3
        )
        self.assertAlmostEqual(
            self.details[2].cycling_infrastructure_ratio(), decimal.Decimal('0.982'), 3
        )

    def test_road_type(self):
        self.assertAlmostEqual(self.details[0].road_type(), decimal.Decimal('0.6'), 1)
        self.assertAlmostEqual(self.details[1].road_type(), decimal.Decimal('0.6'), 1)
        self.assertAlmostEqual(self.details[2].road_type(), decimal.Decimal('1.7'), 1)

    def test_velocity_index(self):
        self.assertAlmostEqual(
            self.details[0].velocity_index(), decimal.Decimal('1.0'), 1
        )
        self.assertAlmostEqual(
            self.details[1].velocity_index(), decimal.Decimal('1.0'), 1
        )
        self.assertAlmostEqual(
            self.details[2].velocity_index(), decimal.Decimal('0.7'), 1
        )

    def test_safety_index(self):
        self.assertAlmostEqual(
            self.details[0].safety_index(), decimal.Decimal('5.3'), 1
        )
        self.assertAlmostEqual(
            self.details[1].safety_index(), decimal.Decimal('5.3'), 1
        )
        self.assertAlmostEqual(
            self.details[2].safety_index(), decimal.Decimal('7.7'), 1
        )

    def test_velocity_index_average(self):
        self.assertAlmostEqual(
            self.sections[0].velocity_index(),
            (self.details[0].velocity_index() + self.details[1].velocity_index()) / 2,
            1,
        )
        self.assertAlmostEqual(
            self.sections[1].velocity_index(), self.details[2].velocity_index(), 1
        )

    def test_safety_index_average(self):
        self.assertAlmostEqual(
            self.sections[0].safety_index(),
            (self.details[0].safety_index() + self.details[1].safety_index()) / 2,
            1,
        )
        self.assertAlmostEqual(
            self.sections[1].safety_index(), self.details[2].safety_index(), 1
        )


class FeedbackTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_feedback(self):
        data = {
            'name': 'Random cyclist',
            'email': 'r.c@example.de',
            'subject': 'Lorem ipsum',
            'message': 'Lorem ipsum dolor sit',
        }
        response = self.client.post(
            '/api/feedback', data=json.dumps(data), content_type='application/json'
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            'From: {} <{}>'.format(data['name'], data['email']),
            mail.outbox[0].message()._payload,
        )
        self.assertIn(
            'Subject: {}'.format(data['subject']), mail.outbox[0].message()._payload
        )
        self.assertIn(data['message'], mail.outbox[0].message()._payload)


class GastroSignupTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_data = {
            'campaign': 'xhain',
            'shop_name': 'Ikonos',
            'category': 'restaurant',
            'first_name': 'Max',
            'last_name': 'Müller',
            'address': 'Böckhstraße 3, 10967 Berlin',
            'email': 'info@ikonos.internet',
            'geometry': {'type': 'Point', 'coordinates': [13.415_941, 52.494_432]},
            'shopfront_length': 480,
            'opening_hours': 'weekend',
            'tos_accepted': True,
        }

        self.registration_data = {
            **self.signup_data,
            'phone': '030123456',
            'usage': 'Schankvorraum',
            'agreement_accepted': True,
            'area': {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [13.417_282_352_175_079, 52.500_718_600_163_28],
                        [13.417_193_839_277_53, 52.500_816_567_976_7],
                        [13.417_057_046_617_8, 52.500_762_685_706_434],
                        [13.417_133_489_575_633, 52.500_667_166_974_18],
                        [13.417_282_352_175_079, 52.500_718_600_163_28],
                    ]
                ],
            },
        }

        self.direct_registration_data = {
            **self.registration_data,
            'certificateS3': 'unit_test_data/test.txt',
        }

    def test_signup(self):
        """
        Test conditions for opening signups
        
        It should only be possible to sign-up when TOGGLE_GASTRO_SIGNUPS is
        set and either no start and end date are defined or the current datetime
        is in that time window.
        """
        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=False
        ):
            response = self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 201)

            signup_id = GastroSignup.objects.first().id
            response2 = self.client.get(f'/api/gastro/xhain/{signup_id}')
            self.assertEqual(response2.status_code, 200)

        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=False, TOGGLE_GASTRO_DIRECT_SIGNUP=False
        ):
            response = self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 405)

        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True,
            TOGGLE_GASTRO_DIRECT_SIGNUP=False,
            GASTRO_SIGNUPS_OPEN=(
                datetime.now(tz=timezone.utc) - timedelta(seconds=30)
            ).isoformat(),
            GASTRO_SIGNUPS_CLOSE=(
                datetime.now(tz=timezone.utc) - timedelta(seconds=5)
            ).isoformat(),
        ):
            response = self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
            self.assertEqual(response.status_code, 405)

    def test_application_readonly_fields(self):
        """Test that changing read-only fields is not possible"""

        # Create a new signup
        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=False
        ):
            self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
        instance = GastroSignup.objects.first()

        # Open signup for application
        instance.status = GastroSignup.STATUS_REGISTRATION
        instance.save()

        readonly_samples = [
            {"status": GastroSignup.STATUS_ACCEPTED},
            {"application_decided": datetime.now(tz=timezone.utc)},
            {"application_received": datetime.now(tz=timezone.utc)},
            {"permit_start": datetime.now(tz=timezone.utc)},
            {"permit_end": datetime.now(tz=timezone.utc)},
        ]

        for sample in readonly_samples:
            # Submit application
            data = self.signup_data
            data.update(sample)
            self.client.put(
                f'/api/gastro/xhain/{instance.id}/{instance.access_key}',
                data=data,
                content_type="application/json",
            )
            instance.refresh_from_db()
            k, v = sample.popitem()
            self.assertNotEqual(getattr(instance, k), v)

    def test_signups_closed(self):
        """Test that changing a submission is only possible if it has the right status"""

        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=False
        ):
            self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
        instance = GastroSignup.objects.first()

        for succeeding_status in [
            GastroSignup.STATUS_REGISTRATION,
            GastroSignup.STATUS_REGISTERED,
        ]:
            instance.status = succeeding_status
            instance.save()

            resp = self.client.put(
                f'/api/gastro/xhain/{instance.id}/{instance.access_key}',
                data=self.registration_data,
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 201, resp.content)

        for failing_status in [
            GastroSignup.STATUS_ACCEPTED,
            GastroSignup.STATUS_REJECTED,
        ]:
            instance.status = failing_status
            instance.save()

            resp = self.client.put(
                f'/api/gastro/xhain/{instance.id}/{instance.access_key}',
                data=self.registration_data,
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 405)

    def test_signup_timestamp(self):
        """Test that the date of signups is recorded on update"""

        # Create a new signup
        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=False
        ):
            self.client.post(
                '/api/gastro/xhain',
                data=json.dumps(self.signup_data),
                content_type='application/json',
            )
        instance = GastroSignup.objects.first()

        # No application date should have been set initially
        self.assertEqual(instance.application_received, None)

        # Open signup for application
        instance.status = GastroSignup.STATUS_REGISTRATION
        instance.save()

        # Submit application
        data = self.signup_data
        resp = self.client.put(
            f'/api/gastro/xhain/{instance.id}/{instance.access_key}',
            data=data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)

        # Test that application was recorded as having been submitted just now
        instance.refresh_from_db()
        self.assertTrue(instance.application_received <= datetime.now(tz=timezone.utc))
        self.assertTrue(
            instance.application_received
            >= (datetime.now(tz=timezone.utc) - timedelta(seconds=5))
        )

    def test_direct_registration(self):
        """Test direct registration"""
        from rest_framework import serializers

        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=True
        ):
            with patch("fixmyapp.serializers.boto3") as boto3:
                boto3.resource.return_value.Object.side_effect = (
                    serializers.ValidationError()
                )
                response = self.client.post(
                    '/api/gastro/xhain',
                    data=json.dumps(self.registration_data),
                    content_type="application/json",
                )
        self.assertEqual(response.status_code, 400, response.data)

        with self.settings(
            TOGGLE_GASTRO_SIGNUPS=True, TOGGLE_GASTRO_DIRECT_SIGNUP=True
        ):
            with patch("fixmyapp.serializers.boto3") as boto3:
                response = self.client.post(
                    '/api/gastro/xhain',
                    data=json.dumps(self.direct_registration_data),
                    content_type="application/json",
                )
                s3 = boto3.resource.return_value
                s3.Object.assert_called_with(
                    settings.AWS_STORAGE_BUCKET_NAME,
                    self.direct_registration_data.get('certificateS3'),
                )
        self.assertEqual(response.status_code, 201)

        instance = GastroSignup.objects.first()

        self.assertTrue(instance.application_received <= datetime.now(tz=timezone.utc))
        self.assertTrue(
            instance.application_received
            >= (datetime.now(tz=timezone.utc) - timedelta(seconds=5))
        )

        self.assertEqual(instance.status, GastroSignup.STATUS_REGISTERED)


class GastroAdminTest(TestCase):
    username = 'test_user'
    password = 'test_password'

    fixtures = ['gastro_signups']

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            self.username, 'test@example.com', self.password
        )

    def test_exportgastrosignups(self):
        """Test exporting Gastro signups"""

        # Test CSV export
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportgastrosignups', f.name, format='csv')
            csv_reader = csv.DictReader(f, dialect='excel')
            self.assertIn(_('geometry'), csv_reader.fieldnames)
            self.assertEqual("Butt", csv_reader.__next__()[_('last name')])

        # Test GeoJSON export
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportgastrosignups', f.name, format='geojson')
            data = json.load(f)
            self.assertEqual('FeatureCollection', data["type"])
            self.assertIn('CRS84', data["crs"]["properties"]["name"])
            self.assertEqual(2, len(data["features"]))
            self.assertEqual("Point", data["features"][0]["geometry"]["type"])
            self.assertIn("shop_name", data["features"][0]["properties"].keys())

        # Test GeoJSON export of area
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportgastrosignups', f.name, '--area', format='geojson')
            data = json.load(f)
            self.assertEqual('FeatureCollection', data["type"])
            self.assertIn('CRS84', data["crs"]["properties"]["name"])
            # Here only one feature is expected because only one signup has area data
            self.assertEqual(1, len(data["features"]))
            self.assertEqual("Polygon", data["features"][0]["geometry"]["type"])
            self.assertIn("shop_name", data["features"][0]["properties"].keys())

    def test_send_notices(self):
        """Test sending notices to applicants"""

        # Both of theses statuses should trigger sending emails
        instances = GastroSignup.objects.all()
        statuses = [GastroSignup.STATUS_ACCEPTED, GastroSignup.STATUS_REJECTED]
        for i, inst in enumerate(instances):
            inst.status = statuses[i]
            inst.save()
            self.assertEqual(inst.status, statuses[i])

        # Need to be signed in as admin user in order to trigger admin actions
        self.client.login(username=self.username, password=self.password)

        # Trigger the admin action by posting this request
        data = {
            'action': 'send_notices',
            '_selected_action': [inst.pk for inst in instances],
        }
        resp = self.client.post(
            reverse('admin:fixmyapp_gastrosignup_changelist'), data=data
        )

        # Sending notice should update the application_decided field
        instances[0].refresh_from_db()
        self.assertTrue(
            (instances[0].application_decided - datetime.now(tz=timezone.utc))
            < timedelta(seconds=5),
            instances[0].application_decided,
        )

        self.assertTrue(
            (instances[0].permit_start == datetime.now(tz=timezone.utc).date()),
            instances[0].permit_start,
        )

        self.assertTrue(
            (
                instances[0].permit_end
                == GastroSignup.CAMPAIGN_DURATION[instances[0].campaign][1]
            ),
            instances[0].permit_end,
        )

        self.assertEqual(resp.status_code, 302, resp.content)
        self.assertEqual(len(mail.outbox), 2, mail.outbox)

    def test_incomplete_applications(self):
        """Test that incomplete applications don't trigger notices to be sent"""

        # Both of theses statuses should trigger sending emails
        instances = GastroSignup.objects.all()

        for i, inst in enumerate(instances):
            inst.status = GastroSignup.STATUS_REJECTED
            if i == 0:
                inst.application_received = None
            if i == 1:
                inst.note = ''
            inst.save()

        # Need to be signed in as admin user in order to trigger admin actions
        self.client.login(username=self.username, password=self.password)

        # Trigger the admin action by posting this request
        data = {
            'action': 'send_notices',
            '_selected_action': [inst.pk for inst in instances],
        }
        resp = self.client.post(
            reverse('admin:fixmyapp_gastrosignup_changelist'), data=data
        )

        self.assertEqual(resp.status_code, 302, resp.content)
        self.assertEqual(len(mail.outbox), 0, mail.outbox)


class GastroRenewalTest(TestCase):
    username = 'test_user'
    password = 'test_password'

    fixtures = ['gastro_signups']

    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            self.username, 'test@example.com', self.password
        )

    def test_offer_renewal(self):
        instances = GastroSignup.objects.all()
        statuses = [GastroSignup.STATUS_ACCEPTED, GastroSignup.STATUS_REJECTED]
        for i, inst in enumerate(instances):
            inst.status = statuses[i]
            inst.save()

        # Need to be signed in as admin user in order to trigger admin actions
        self.client.login(username=self.username, password=self.password)

        # Trigger the admin action by posting this request
        data = {
            'action': 'send_renewal_offer',
            '_selected_action': [inst.pk for inst in instances],
        }
        resp = self.client.post(
            reverse('admin:fixmyapp_gastrosignup_changelist'), data=data
        )

        for inst in instances:
            inst.refresh_from_db()
            self.assertTrue(inst.renewal_sent_on is not None)

        self.assertEqual(resp.status_code, 302, resp.content)
        self.assertEqual(len(mail.outbox), 2, mail.outbox)

        # Regression test for email recipeint being application email address
        # (`mail.outbox` is in reverse order of the instances)
        for i, inst in enumerate(instances[::-1]):
            self.assertEqual(inst.email, mail.outbox[i].to[0])

    @override_settings(EMAIL_BACKEND='fixmyapp.tests.FailingMockEmailBackend')
    def test_offer_renewal_invalid_email(self):
        inst = GastroSignup.objects.first()
        inst.status = GastroSignup.STATUS_ACCEPTED
        inst.email = 'test@me.not; secondemail@otherdomain.net'
        inst.save()

        self.client.login(username=self.username, password=self.password)
        resp = self.client.post(
            reverse('admin:fixmyapp_gastrosignup_changelist'),
            data={'action': 'send_renewal_offer', '_selected_action': [inst.pk]},
        )

        # This action should result in two email messages, one with the error
        # and another one to inform about zero emails having been sent
        msgs = list(resp.context['messages'])
        self.assertEqual(len(msgs), 2, msgs)
        self.assertEqual(msgs[0].level, messages.ERROR, msgs[0])

        # However, the response should still be successful and no email sent
        self.assertEqual(resp.status_code, 302, resp.content)
        self.assertEqual(len(mail.outbox), 0, mail.outbox)

    def test_accept_renewal(self):
        instance = GastroSignup.objects.first()
        instance.status = GastroSignup.STATUS_ACCEPTED
        instance.save()

        endpoint = (
            f"/api/gastro/{instance.campaign}/renewal/{instance.id}/invalid_access_key"
        )
        resp = self.client.post(endpoint, content_type="application/json")
        self.assertEqual(resp.status_code, 401)

        endpoint = f"/api/gastro/{instance.campaign}/renewal/{instance.id}/{instance.access_key_renewal}"
        resp = self.client.post(endpoint, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        instance.refresh_from_db()
        renewal = instance.renewal_application
        self.assertEqual(renewal.shop_name, instance.shop_name)
        self.assertEqual(
            renewal.campaign, GastroSignup.RENEWAL_CAMPAIGN[instance.campaign]
        )
        self.assertTrue(
            renewal.application_received - datetime.now(tz=timezone.utc)
            < timedelta(seconds=5)
        )
        self.assertTrue(renewal.renewal_sent_on is None)


class PlaystreetTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "campaign": "xhain",
            "first_name": "Max",
            "last_name": "Mustermann",
            "email": "max@mustermann.de",
            "tos_accepted": True,
            "captain": False,
            "message": "",
            "street": "Bergmannstraße",
        }

    def test_signup(self):
        response = self.client.put(
            '/api/playstreets/xhain',
            data=json.dumps(self.data),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)

    def test_listing(self):
        self.client.put(
            '/api/playstreets/xhain',
            data=json.dumps(self.data),
            content_type='application/json',
        )
        response = self.client.get('/api/playstreets/xhain')
        self.assertEqual(response.status_code, 200)
        rv = response.json()
        self.assertTrue(len(rv.items()) > 0)
        sample = rv.popitem()
        self.assertTrue(isinstance(sample[0], str))
        self.assertTrue(isinstance(sample[1], int))

    def test_export_signups(self):
        self.client.put(
            '/api/playstreets/xhain',
            data=json.dumps(self.data),
            content_type='application/json',
        )
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportplaystreets', f.name)
            csv_reader = csv.DictReader(f, dialect='excel')
            self.assertIn('Spielstraße', csv_reader.fieldnames)


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


class LikeTest(object):
    def setUp(self):
        get_user_model().objects.create_user('foo', 'foo@example.org', 'bar')
        self.client = Client()
        self.credentials = {'username': 'foo', 'password': 'bar'}

    def test_get_like(self):
        response = self.client.get(self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_get_like_as_anonymous(self):
        response = self.client.get(self.likes_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def test_post_like(self):
        response = self.client.post(self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {'user_has_liked': True, 'likes': 1})

        response = self.client.get(
            self.liked_by_user_url, **self._get_authorization_header()
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('count'), 1)
        self.assertIn('results', response.json())
        self.assertTrue(
            response.json().get('results')[0].get('url').endswith(self.instance_url)
        )

        response = self.client.post(self.likes_url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user_has_liked': False, 'likes': 0})

    def _get_authorization_header(self):
        response = self.client.post(
            '/api/jwt/create/',
            json.dumps(self.credentials),
            content_type='application/json',
        )
        return {'HTTP_AUTHORIZATION': 'JWT ' + response.json()['access']}


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class LikeProjectTest(LikeTest, TestCase):
    def setUp(self):
        self.instance = Project.objects.create(title='Lorem ipsum', side=Project.BOTH)
        self.instance_url = reverse('project-detail', kwargs={'pk': self.instance.id})
        self.likes_url = reverse('likes-projects', kwargs={'pk': self.instance.id})
        self.liked_by_user_url = reverse('projects-liked-by-user')
        super(LikeProjectTest, self).setUp()


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class LikeReportTest(LikeTest, TestCase):
    def setUp(self):
        self.instance = Report.objects.create(
            address='Potsdamer Platz 1',
            description='Lorem ipsum dolor sit',
            geometry=Point(13.346_355_406_363_18, 52.525_659_903_336_57),
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
        response = self.client.post(self.url, **self._get_authorization_header())
        self.assertEqual(response.status_code, 204)

    def _get_authorization_header(self):
        response = self.client.post(
            '/api/jwt/create/',
            json.dumps(self.credentials),
            content_type='application/json',
        )
        return {'HTTP_AUTHORIZATION': 'JWT ' + response.json()['access']}


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class ViewsTest(TestCase):

    fixtures = ['projects', 'sections', 'sectiondetails']

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
    fixtures = ['sections', 'sectiondetails']

    def test_exportsections(self):
        with tempfile.NamedTemporaryFile() as f:
            call_command('exportsections', f.name)
            export = json.load(f)
            self.assertEqual(export.get('type'), 'FeatureCollection')
            self.assertEqual(type(export.get('features')), list)
            self.assertEqual(len(export.get('features')), 5)
