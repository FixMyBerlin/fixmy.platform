import argparse
import csv
import json
from datetime import datetime
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from reports.models import Report

FIELDNAMES = [
    'id',
    'origin_ids',
    'url',
    'likes',
    'status',
    'address',
    'description',
    'created',
    'status_reason',
    'long',
    'lat',
    'number',
    'fee_acceptable',
]


def format_origin_ids(origins):
    return ';'.join([str(o.id) for o in origins])


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
        csv_writer.writeheader()

        for report in query:
            row_data = model_to_dict(report, fields=FIELDNAMES)
            row_data['created'] = report.created_date.isoformat()
            row_data['long'] = report.geometry.x
            row_data['lat'] = report.geometry.y
            row_data['number'] = report.bikestands.number
            row_data['fee_acceptable'] = report.bikestands.fee_acceptable is True
            row_data['likes'] = report.likes.count()
            row_data['url'] = report.frontend_url
            row_data['origin_ids'] = format_origin_ids(report.origin.all())
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
                        "origin_ids": format_origin_ids(report.origin.all()),
                        "address": report.address,
                        "created": report.created_date.isoformat(),
                        "description": report.description,
                        "fee_acceptable": report.bikestands.fee_acceptable is True,
                        "id": report.id,
                        "likes": report.likes.count(),
                        "number": report.bikestands.number,
                        'status': report.status,
                        "status_reason": report.status_reason,
                        "url": report.frontend_url,
                        'subject': 'BIKE_STANDS',
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [report.geometry.x, report.geometry.y],
                    },
                }
            )

        json.dump(results, target_file, ensure_ascii=False, indent=2)
