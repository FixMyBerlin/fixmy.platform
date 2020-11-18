import csv
import json
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from unittest.mock import patch

from fixmyapp.models import Like
from reports.models import Report, BikeStands, StatusNotice
from .commands.importreports import create_report_plannings, link_report_origins


class ExportReports(TestCase):
    fixtures = ['user', 'reports', 'plannings']

    cols = [
        'id',
        'origin_ids',
        'status',
        'address',
        'description',
        'status_reason',
        'number',
    ]

    def _check_assertions(self, exported):
        source = Report.objects.get(pk=exported['id'])
        self.assertEqual(exported['origin_ids'], '1')
        self.assertEqual(exported['url'], source.frontend_url)
        self.assertEqual(int(exported['likes']), 0)
        self.assertEqual(exported['status'], source.status)
        self.assertEqual(exported['address'], source.address)
        self.assertEqual(exported['description'], source.description)
        self.assertEqual(exported['created'], source.created_date.isoformat())
        self.assertEqual(exported['status_reason'], source.status_reason)
        self.assertEqual(int(exported['number']), source.bikestands.number)
        self.assertTrue(exported['fee_acceptable'] in [False, 'False'])

    def test_export_reports_csv(self):
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='csv')
            csv_reader = csv.DictReader(f, dialect='excel')
            for col in self.cols + ['long', 'lat']:
                self.assertIn(col, csv_reader.fieldnames)
            # select a planning entry to test export of origin ids
            exported = [r for r in csv_reader if r['id'] == '3'][0]
            self._check_assertions(exported)
            self.assertTrue(50 < float(exported['lat']) < 60)
            self.assertTrue(0 < float(exported['long']) < 10)

    def test_export_reports_geojson(self):
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='geojson')
            data = json.load(f)
            for col in self.cols:
                self.assertIn(col, data["features"][0]["properties"].keys())
            exported = [r for r in data["features"] if r['properties']['id'] == 3][0][
                'properties'
            ]
            self._check_assertions(exported)


class ImportReports(TestCase):
    fixtures = ['user', 'reports', 'plannings']

    def test_import_export_integration_for_inserting(self):
        """Test exporting as CSV and then filling empty db from exported file"""
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='csv'
        ) as f:
            call_command('exportreports', f.name, format='csv')
            Report.objects.all().delete()
            f.seek(0)

            # the export contains id values for each row so importing should
            # not work without `force_insert`
            with patch('sys.exit') as mock_sys_exit:
                call_command('importreports', f.name)
                mock_sys_exit.assert_called_with(1)
            
            call_command('importreports', f.name, force_insert=True)

        self.assertEqual(Report.objects.all().count(), 4, f"Got {Report.objects.all()}")
        report = Report.objects.get(pk=3)
        self.assertEqual(report.origin.count(), 1, report.origin.all())
        

    def test_import_export_integration_for_updating(self):
        """Text exporting as CSV and then updating entries from exported file"""
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='csv'
        ) as f:
            call_command('exportreports', f.name, format='csv')
            report = BikeStands.objects.get(pk=3)
            report.address = 'Test'
            report.origin.clear()
            report.save()
            call_command('importreports', f.name)

        report.refresh_from_db()
        self.assertTrue(report.address != 'Test')
        self.assertEqual(report.origin.count(), 1, report.origin.all())

    def test_load_reports_does_not_exist(self):
        """Try linking to nonexistent origin id"""
        reports = Report.objects.all()
        rows = [
            {'id': r.id, 'origin_ids': ';'.join([str(o.id) for o in r.origin.all()])}
            for r in reports
        ]
        rows[0]['origin_ids'] = '9999'
        self.assertRaises(ValueError, link_report_origins, rows)

    def test_origin_author_notification(self):
        """Test that origin authors get notices"""
        planning = Report.objects.get(pk=3)
        planning.status = Report.STATUS_DONE
        planning.save()

        # Make sure that the notice is not created for the author but for the
        # origin author
        self.assertTrue(planning.user is None)

        origin_user = planning.origin.first().user
        self.assertEqual(1, StatusNotice.objects.filter(user=origin_user).count())

    def test_fix_origin_status(self):
        """Test check for valid origin status when linking origin"""
        test_report = Report.objects.get(pk=1)
        test_report.status = Report.STATUS_REPORT_NEW
        test_report.save()

        rows = [
            {'id': r.id, 'origin_ids': ';'.join([str(o.id) for o in r.origin.all()])}
            for r in Report.objects.all()
        ]
        self.assertRaises(ValueError, link_report_origins, rows)
        try:
            link_report_origins(rows, fix_status=True)
        except ValueError:
            self.fail('Raised ValueError despite `fix_status` param')

class SendNotifications(TestCase):
    fixtures = ['user', 'reports', 'plannings']

    def setUp(self):
        super().setUp()
        self.planning = Report.objects.get(pk=4)
        self.assertTrue(self.planning.user is None)
        self.report = Report.objects.get(pk=2)
        self.assertTrue(self.report.user is not None)

    def test_notice_anonymous_report(self):
        """No notice is created when reports are saved that have no author (user)"""
        self.planning.origin.set([])
        self.planning.status = Report.STATUS_REPORT_VERIFICATION
        self.planning.save()
        self.assertEqual(StatusNotice.objects.count(), 0)

    def test_notice_liked(self):
        """A notice is created for liked reports"""
        user = self.report.user
        ct = ContentType.objects.get_for_model(Report)
        like = Like.objects.create(
            content_type=ct, object_id=self.planning.id, user=user
        )
        self.planning.status = Report.STATUS_REPORT_VERIFICATION
        self.planning.save()
        self.assertEqual(StatusNotice.objects.filter(user=user).count(), 1)

    def test_notice_author(self):
        """A notice is created for report authors"""
        self.report.status = Report.STATUS_REPORT_INACTIVE
        self.report.save()
        self.assertEqual(StatusNotice.objects.count(), 1)

    def test_notice_planning(self):
        """A notice is created for authors of reports linked to plannings"""
        self.planning.status = Report.STATUS_EXECUTION
        self.planning.save()
        self.assertTrue(self.planning.user is None)
        self.assertEqual(StatusNotice.objects.count(), 1)

    def test_sendnotifications(self):
        """Test every block in the template for notification emails"""
        # Create a second report to use in testing
        report, report2 = Report.objects.filter(status=Report.STATUS_REPORT_ACCEPTED)
        planning, planning2 = Report.objects.exclude(
            status=Report.STATUS_REPORT_ACCEPTED
        )

        # Assign a status other than those used below so that changing the status
        # will actually enqueue notices
        for p in (report, report2, planning, planning2):
            p.status = Report.STATUS_INVALID
            p.save()

            # Reset the report's internally noted previous status. This field
            # is usually set to the current status whenever the object is loaded
            # However, here the object's status is changed after loading so this
            # field has to be set in order to pretend that it was originally
            # loaded with this status.
            p._Report__prev_status = Report.STATUS_INVALID

        # Test command without something to send
        call_command('sendnotifications')
        self.assertEqual(0, len(mail.outbox))

        # Test that no email is sent when changing the status to one that is
        # not represented in the notification emails
        report.status = Report.STATUS_INVALID
        report.save()
        call_command('sendnotifications')
        self.assertEqual(0, len(mail.outbox))

        for update_multiple in [True, False]:
            reports = [report, report2] if update_multiple else [report]
            plannings = [planning, planning2] if update_multiple else [planning]

            for status in [
                Report.STATUS_REPORT_REJECTED,
                Report.STATUS_REPORT_ACCEPTED,
            ]:
                StatusNotice.objects.all().delete()
                self.assertEqual(0, len(mail.outbox))
                for r in reports:
                    r.status = status
                    r.save()

                call_command('sendnotifications')
                self.assertEqual(StatusNotice.objects.filter(sent=False).count(), 0)
                self.assertEqual(1, len(mail.outbox))
                for r in reports:
                    for variant in mail.outbox[0].message()._payload:
                        # report address is included in email message
                        self.assertIn(r.address, str(variant))
                        # there is always at least one report link plus the
                        # unsubscribe link included in the message
                        # self.assertTrue(str(variant).count("http") >= 2)

                    if status == Report.STATUS_REPORT_ACCEPTED:
                        for p in r.plannings.all():
                            # For reports with the `report_accepted` status,
                            # references to the linked planning are also included
                            self.assertIn(
                                p.address, str(mail.outbox[0].message()._payload[1])
                            )
                mail.outbox = []

            for status in [
                Report.STATUS_PLANNING,
                Report.STATUS_EXECUTION,
                Report.STATUS_DONE,
            ]:
                StatusNotice.objects.all().delete()
                for p in [planning, planning2]:
                    p.status = status
                    p.save()

                call_command('sendnotifications')
                self.assertEqual(StatusNotice.objects.filter(sent=False).count(), 0)
                self.assertEqual(1, len(mail.outbox))
                for p in plannings:
                    for variant in mail.outbox[0].message()._payload:
                        self.assertIn(p.address, str(variant))
                        # self.assertTrue(str(variant).count("http") >= 2)
                mail.outbox = []

    def test_notification_preference(self):
        """Notifications should not be sent after user has disabled them"""
        # Enqueue a notice
        self.report.status = Report.STATUS_REPORT_ACCEPTED
        self.report.save()
        user = self.report.user
        self.assertEqual(StatusNotice.user_preference(user), True)
        resp = Client().get(StatusNotice.unsubscribe_url(user))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(StatusNotice.user_preference(user), False)
        call_command('sendnotifications')
        self.assertEqual(0, len(mail.outbox))
        self.assertEqual(0, StatusNotice.objects.filter(user=user).count())

    def test_sample_email(self):
        """Test helper option used to preview email contents"""
        num_entries = Report.objects.count()
        call_command('sendnotifications', send_samples='bar@baz.com')
        self.assertEqual(3, len(mail.outbox))
        self.assertEqual(Report.objects.count(), num_entries)

    def test_staff_only(self):
        """Test option to send notifications only for staff users"""
        self.report.status = Report.STATUS_EXECUTION
        self.report.save()
        call_command('sendnotifications', '--staff-only')
        self.assertEqual(0, len(mail.outbox))
        self.report.user.is_staff = True
        self.report.user.save()
        call_command('sendnotifications', '--staff-only')
        self.assertEqual(1, len(mail.outbox))
