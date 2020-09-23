import argparse
import csv
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from pinax.notifications.models import send_now

from reports.models import Report

FIELDNAMES = [
    'id',
    'address',
    'description',
    'number',
    'fee_acceptable',
    'created',
    'likes',
    'status',
    'status_reason',
    'position',
]

FIELDNAMES_DE = [_(entry) for entry in FIELDNAMES]


class Command(BaseCommand):
    help = 'Export published reports'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            type=argparse.FileType('w', encoding='UTF-8'),
            help='output filename',
        )
        parser.add_argument(
            '--format', choices=['csv', 'geojson'], help='choose a format to use'
        )

    def handle(self, *args, **options):
        query = Report.objects.order_by('id').prefetch_related('likes', 'bikestands')
        if options['format'] == 'csv':
            self.export_csv(query, options['filename'])
        else:
            self.export_geojson(query, options['filename'])

    def export_csv(self, query, target_file):

        csv_writer = csv.DictWriter(target_file, fieldnames=FIELDNAMES, dialect='excel')

        # Write table headers using German translation
        csv_writer.writerow(dict(zip(FIELDNAMES, FIELDNAMES_DE)))

        for report in query:
            row_data = model_to_dict(report, fields=FIELDNAMES)
            row_data['created'] = report.created_date.isoformat()
            row_data["position"] = f"{report.geometry.y},{report.geometry.x}"
            row_data['number'] = report.bikestands.number
            row_data['fee_acceptable'] = report.bikestands.fee_acceptable is True

            csv_writer.writerow(row_data)

    def export_geojson(self, query, target_file):
        results = {
            "type": "FeatureCollection",
            "name": f"reports export {datetime.now().isoformat()}",
            'features': [],
        }

        for report in query:
            results["features"].append(
                {
                    "type": "Feature",
                    "properties": {
                        "address": report.address,
                        "created_date": report.created_date.isoformat(),
                        "description": report.description,
                        "fee_acceptable": report.bikestands.fee_acceptable is True,
                        "id": report.id,
                        "likes": report.likes.count(),
                        "number": report.bikestands.number,
                        'status': report.status,
                        "status_reason": report.status_reason,
                        'subject': 'BIKE_STANDS',
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [report.geometry.x, report.geometry.y],
                    },
                }
            )

        json.dump(results, target_file, ensure_ascii=False, indent=2)
