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


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class CommandTest(TestCase):
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


class ExportReports(CommandTest):
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


class ImportReports(CommandTest):
    def setUp(self):
        super().setUp()
        self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
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
        self.assertEqual(len(reports), 1)
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
        self.assertEqual(len(reports), 1)


class ImportReportPlannings(CommandTest):
    def setUp(self):
        super().setUp()
        # set id explicitly in order to be to reference it below in `origin_ids`
        self.data['id'] = 1
        resp = self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        self.report_id = resp.data['id']
        self.plannings = [
            {
                'origin_ids': str(resp.data['id']),
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
        self.assertRaises(BikeStands.DoesNotExist, create_report_plannings, rows)


class SendNotifications(ImportReportPlannings):
    # Command test is inheriting from ImportReportPlannings because it is
    # part of the same process (import planning data, then sending notifications)
    # about it, so test data can be reused.

    def test_notice_anonymous_report(self):
        """No notice is created when reports are saved that have no author (user)"""
        report = Report.objects.get(pk=self.report_id)
        report.status = Report.STATUS_REPORT_VERIFICATION
        report.save()
        self.assertEqual(StatusNotice.objects.count(), 0)

    def test_notice_liked(self):
        """A notice is created for liked reports"""
        report = Report.objects.get(pk=self.report_id)
        ct = ContentType.objects.get_for_model(Report)
        like = Like.objects.create(content_type=ct, object_id=report.id, user=self.user)
        report.status = Report.STATUS_REPORT_VERIFICATION
        report.save()
        self.assertEqual(StatusNotice.objects.count(), 1)

    def test_notice_author(self):
        """A notice is created for report authors"""
        report = Report.objects.get(pk=self.report_id)
        report.user = self.user
        report.status = Report.STATUS_REPORT_INACTIVE
        report.save()
        assert report.likes.count() == 0
        self.assertEqual(StatusNotice.objects.count(), 1)

    def test_notice_planning(self):
        """A notice is created for authors of reports linked to plannings"""
        report = Report.objects.get(pk=self.report_id)
        report.user = self.user
        report.save()
        planning = list(create_report_plannings(self.plannings))[0]
        planning.status = Report.STATUS_EXECUTION
        planning.save()
        self.assertEqual(StatusNotice.objects.count(), 1)

    def test_send_notifications(self):
        # Create a second report to use in testing
        resp = self.client.post(
            '/api/reports', data=json.dumps(self.data), content_type='application/json'
        )
        report_2_id = resp.data['id']

        # Prepare two planning entries with statuses other than all the statuses
        # that will be tested below
        self.plannings[0]['status'] = 'invalid'
        self.plannings.append(self.plannings[0])

        # Change one of the plannings' address so that we can check whether
        # each planning's address is included in the outgoing emails
        self.plannings[1]['address'] += "(2)"
        self.plannings[1]['origin_ids'] = str(report_2_id)
        create_report_plannings(self.plannings)
        planning, planning2 = Report.objects.filter(status=Report.STATUS_INVALID).all()

        # Associate a user with each report so that notifications will be
        # sent for them
        report, report2 = [p.origin.first() for p in (planning, planning2)]
        for r in report, report2:
            r.user = self.user
            r.save()

        # Test command without something to send
        call_command('send_notifications')
        self.assertEqual(0, len(mail.outbox))

        for update_multiple in [True, False]:
            reports = [report, report2] if update_multiple else [report]
            plannings = [planning, planning2] if update_multiple else [planning]

            for status in [
                Report.STATUS_REPORT_REJECTED,
                Report.STATUS_REPORT_ACCEPTED,
            ]:
                for r in reports:
                    r.status = status
                    r.save()

                call_command('send_notifications')
                self.assertEqual(StatusNotice.objects.filter(sent=False).count(), 0)
                self.assertEqual(1, len(mail.outbox))
                for r in reports:
                    self.assertIn(r.address, mail.outbox[0].message()._payload)
                mail.outbox = []

            for status in [
                Report.STATUS_PLANNING,
                Report.STATUS_EXECUTION,
                Report.STATUS_DONE,
            ]:
                for p in [planning, planning2]:
                    p.status = status
                    p.save()

                call_command('send_notifications')
                self.assertEqual(StatusNotice.objects.filter(sent=False).count(), 0)
                self.assertEqual(1, len(mail.outbox))
                for p in plannings:
                    self.assertIn(p.address, mail.outbox[0].message()._payload)
                mail.outbox = []

    def test_notification_preference(self):
        """Notifications should not be sent after user has disabled them"""
        # Enqueue a notice
        report = Report.objects.get(pk=self.report_id)
        report.user = self.user
        report.status = Report.STATUS_REPORT_ACCEPTED
        report.save()
        self.assertEqual(StatusNotice.user_preference(self.user), True)
        resp = self.client.get(StatusNotice.unsubscribe_url(self.user))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(StatusNotice.user_preference(self.user), False)
        call_command('send_notifications')
        self.assertEqual(0, len(mail.outbox))
        self.assertEqual(0, StatusNotice.objects.filter(user=self.user).count())
