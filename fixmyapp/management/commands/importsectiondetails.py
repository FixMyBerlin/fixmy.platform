from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.models import Photo, SectionDetails
import argparse
import csv
import sys

mapping = {
    'MetaID': 'section_id',
    'side': 'side',
    'tempolimit': 'speed_limit',
    'dailytraffic': 'daily_traffic',
    'dailytraffic_heavy': 'daily_traffic_heavy',
    'daily_traffic_transporter': 'daily_traffic_cargo',
    'dailiy_traffic_bus': 'daily_traffic_bus',
    'length': 'length',
    'no_crossing': 'crossings',
    'card_pt': 'orientation',
    'RVA1': 'rva1',
    'RVA2': 'rva2',
    'RVA3': 'rva3',
    'RVA4': 'rva4',
    'RVA5': 'rva5',
    'RVA6': 'rva6',
    'RVA7': 'rva7',
    'RVA8': 'rva8',
    'RVA9': 'rva9',
    'RVA10': 'rva10',
    'RVA11': 'rva11',
    'RVA12': 'rva12',
    'RVA13': 'rva13',
}


class Command(BaseCommand):
    help = 'Imports section details'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            default=sys.stdin,
            help='A CSV file'
        )

    def handle(self, *args, **options):
        SectionDetails.objects.all().delete()
        reader = csv.DictReader(options['file'])
        for row in (row for row in reader if row['exist'] == '1'):
            kwargs = {
                mapping[key]: row[key].replace(',', '.') for key in mapping
            }
            try:
                obj, created = SectionDetails.objects.update_or_create(**kwargs)
                for path in row['rva_pics'].split():
                    photo = Photo(
                        content_object=obj,
                        copyright='Geoportal Berlin / Radverkehrsanlagen',
                        src='rva_pics{}'.format(path)
                    )
                    photo.save()
            except IntegrityError as e:
                message = 'Referenced section with MetaID {} does not exist.'.format(row['MetaID'])
                self.stderr.write(message)
