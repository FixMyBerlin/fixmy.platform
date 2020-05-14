from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from datetime import datetime
from fixmyapp.models import GastroSignup
import argparse
import csv
import json

FIELDNAMES = {
    'shop_name': _('shop name'),
    'address': _('address'),
    'location': _('geometry'),
    'shopfront_length': _('shopfront length'),
    'first_name': _('first name'),
    'last_name': _('last name'),
    'email': _('email'),
    'category': _('category'),
    'created_date': 'Eingereicht',
    'status': _('status'),
    'tos_accepted': _('tos_accepted'),
    'id': _('Kennziffer'),
}


class Command(BaseCommand):
    help = 'Export signups for gastro streets'

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
        query = GastroSignup.objects.order_by('address', 'shop_name')
        if options['format'] == 'csv':
            self.export_csv(query, options['filename'])
        else:
            self.export_geojson(query, options['filename'])

    def export_csv(self, query, target_file):
        csv_writer = csv.DictWriter(
            target_file, fieldnames=FIELDNAMES.keys(), dialect='excel'
        )

        # Write table headers using German translation
        csv_writer.writerow(FIELDNAMES)

        for report in query:
            row_data = model_to_dict(report, fields=FIELDNAMES.keys())
            row_data['created_date'] = date_format(
                report.created_date, format='DATETIME_FORMAT', use_l10n=True
            )
            row_data['tos_accepted'] = 'Ja' if report.tos_accepted else 'Nein'
            row_data["location"] = f"{report.geometry.y},{report.geometry.x}"

            csv_writer.writerow(row_data)

    def export_geojson(self, query, target_file):
        results = {
            "type": "FeatureCollection",
            "name": f"gastro signups export {datetime.now().isoformat()}",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            'features': [],
        }

        for entry in query:
            results["features"].append(
                {
                    "type": "Feature",
                    "properties": {
                        "shop_name": entry.shop_name,
                        "address": entry.address,
                        "created_date": entry.created_date.isoformat(),
                        "shopfront_length": entry.shopfront_length,
                        "first_name": entry.first_name,
                        "last_name": entry.last_name,
                        "email": entry.email,
                        "category": entry.category,
                        'status': entry.status,
                        'tos_accepted': entry.tos_accepted,
                        "id": entry.id,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [entry.geometry.x, entry.geometry.y],
                    },
                }
            )

        json.dump(results, target_file, ensure_ascii=False, indent=2)
