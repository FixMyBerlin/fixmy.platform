from django.core.management.base import BaseCommand
from fixmyapp.models import PlanningSection, PlanningSectionDetails
import argparse
import csv
import sys

mapping = {
    'side': 'side',
    'tempolimit': 'speed_limit',
    'dailytraffic': 'daily_traffic',
    'dailytraffic_heavy': 'daily_traffic_heavy',
    'dailytraffic_transporter': 'daily_traffic_cargo',
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
    help = 'Imports planning section details'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            default=sys.stdin,
            help='A CSV file'
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.'
        )

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'])
        for row in reader:
            kwargs = {}
            for key in mapping:
                kwargs[mapping[key]] = row[key].replace(',', '.')

            psd, created = PlanningSectionDetails.objects.get_or_create(
                planning_section_id=row['MetaID'], **kwargs)

            psd.save()
