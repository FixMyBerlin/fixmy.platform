import csv
import json
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from fixmyapp.models import Like
from reports.models import Report, BikeStands, StatusNotice
from .commands.importreportplannings import create_report_plannings


class ExportReports(TestCase):
    fixtures = ['user', 'reports']

    def test_export_reports_csv(self):
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='csv')
            csv_reader = csv.DictReader(f, dialect='excel')
            self.assertIn('ID', csv_reader.fieldnames)

    def test_export_reports_geojson(self):
        with tempfile.NamedTemporaryFile(mode="w+", encoding="UTF-8") as f:
            call_command('exportreports', f.name, format='geojson')
            data = json.load(f)
            self.assertIn('id', data["features"][0]["properties"].keys())


class ImportReports(TestCase):
    fixtures = ['user', 'reports']

    def setUp(self):
        super().setUp()
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f:
            call_command('exportreports', f.name, format='geojson')
            self.export_data = json.load(f)

        self.export_data["features"][0]["properties"]["address"] = "test"
        self.export_data["features"][0]["properties"]["number"] = 1

    def test_update_reports(self):
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f1:
            json.dump(self.export_data, f1)
            f1.seek(0)
            call_command('importreports', f1.name)

        reports = Report.objects.all()
        self.assertEqual(len(reports), 2)
        self.assertEqual(reports[0].address, 'test')
        self.assertEqual(reports[0].bikestands.number, 1)

    def test_insert_reports(self):
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='geojson'
        ) as f2:
            json.dump(self.export_data, f2)
            Report.objects.all().delete()
            f2.seek(0)
            call_command('importreports', f2.name)

        reports = Report.objects.all()
        self.assertEqual(len(reports), 2)


class ImportReportPlannings(TestCase):
    fixtures = ['user', 'reports']

    def setUp(self):
        # Make sure that report has a status that is valid for linking to
        # a planning
        self.report = Report.objects.first()
        self.report.status = Report.STATUS_REPORT_ACCEPTED
        self.report.save()

        self.plannings = [
            {
                'origin_ids': str(self.report.id),
                'address': 'Vereinsstrasse 19, Aachen',
                'geometry': '6.09284, 50.76892',
                'description': '(für Besucher)',
                'status': 'planning',
                'status_reason': '',
                'number': 5,
            }
        ]

    def test_load_reports(self):
        reports = list(create_report_plannings(self.plannings))
        assert len(reports) == 1
        assert reports[0].origin.count() == 1

    def test_load_reports_does_not_exist(self):
        """Try linking to nonexistent origin id"""

        rows = self.plannings
        rows[0]['origin_ids'] = '9999'
        self.assertRaises(ValueError, create_report_plannings, rows)

    def test_origin_author_notification(self):
        """Test that origin authors get notices"""
        planning = list(create_report_plannings(self.plannings))[0]
        planning.status = Report.STATUS_DONE
        planning.save()
        self.assertTrue(planning.user is None)
        self.assertEqual(1, StatusNotice.objects.filter(user=self.report.user).count())

    def test_repeated_execution(self):
        """Test that additional entries are created on re-run"""
        create_report_plannings(self.plannings)
        create_report_plannings(self.plannings)
        self.assertEqual(BikeStands.objects.count(), 4)

    def test_fix_origin_status(self):
        self.report.status = Report.STATUS_REPORT_NEW
        self.report.save()
        reports = list(create_report_plannings(self.plannings, force=True))
        assert reports[0].origin.first().status == Report.STATUS_REPORT_ACCEPTED


class SendNotifications(TestCase):
    fixtures = ['user', 'reports', 'plannings']

    def setUp(self):
        super().setUp()
        self.planning = Report.objects.get(pk=1821)
        self.assertTrue(self.planning.user is None)
        self.report = Report.objects.get(pk=1822)
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
                        self.assertTrue(str(variant).count("http") >= 2)

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
                for p in [planning, planning2]:
                    p.status = status
                    p.save()

                call_command('sendnotifications')
                self.assertEqual(StatusNotice.objects.filter(sent=False).count(), 0)
                self.assertEqual(1, len(mail.outbox))
                for p in plannings:
                    for variant in mail.outbox[0].message()._payload:
                        self.assertIn(p.address, str(variant))
                        self.assertTrue(str(variant).count("http") >= 2)
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
