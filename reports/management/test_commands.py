import csv
import json
import tempfile
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings

from reports.models import Report
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
        self.origin_id = resp.data['id']

    def test_load_reports(self):
        rows = [
            {
                'origin_ids': str(self.origin_id),
                'address': 'Vereinsstraße 19, Aachen',
                'geometry': '6.09284, 50.76892',
                'description': '(für Besucher)',
                'status': 'planning',
                'status_reason': '',
                'number': 5,
            }
        ]
        reports = list(create_report_plannings(rows))
        assert len(reports) == 1
        assert reports[0].origin.count() == 1
