from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from fixmyapp.models import Report, BikeStands
import argparse
import csv
import logging
import json

logger = logging.getLogger(__name__)

FIELDNAMES = [
    'id',
    'address',
    'description',
    'Anzahl gewünscht',
    'likes',
    'status',
    'status_reason',
    'Position',
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
            row_data["Position"] = f"{report.geometry.y},{report.geometry.x}"

            bike_stands = BikeStands.objects.filter(report_ptr=report)
            if len(bike_stands) > 0:
                row_data['Anzahl gewünscht'] = bike_stands[0].number

            csv_writer.writerow(row_data)

    def export_geojson(self, query, target_file):
        results = {
            "type": "FeatureCollection",
            "name": 'Reports export',
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            'features': [],
        }
        for report in query:
            bike_stands = BikeStands.objects.filter(report_ptr=report)
            results["features"].append(
                {
                    "type": "Feature",
                    "properties": {
                        "subject": "BIKE_STANDS",
                        "fee_acceptable": False
                        if len(bike_stands) == 0
                        else bike_stands[0].fee_acceptable is True,
                        "number": 0 if len(bike_stands) == 0 else bike_stands[0].number,
                        "description": report.description,
                        "address": report.address,
                        "created": report.created_date.isoformat(),
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [report.geometry.y, report.geometry.x],
                    },
                }
            )

        json.dump(results, target_file, ensure_ascii=False)
