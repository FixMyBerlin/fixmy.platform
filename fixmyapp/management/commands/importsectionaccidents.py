import json
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.models import SectionAccidents
import argparse
import csv
import sys


# CSV col name -> model field name
MAPPING = {
    'section_id': 'section_id',
    'side': 'side',
    'killed': 'killed',
    'severely_injured': 'severely_injured',
    'slightly_injured': 'slightly_injured',
    'source': 'source',
    'risk_level': 'risk_level',
}


class Command(BaseCommand):
    help = 'Import an accident dataset for existing sections'
    output_transaction = True
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            default=sys.stdin,
            help='A CSV file',
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            dest='skip_confirmation',
            help='skip confirmation before overwriting data',
        )

    def handle(self, *args, **options):
        data = list(csv.DictReader(options['file']))

        prompt = f'Delete all accident data sets and import {len(data)} new data sets?'
        if options['skip_confirmation'] is False:
            if input(prompt) != '':
                self.stdout.write('Import cancelled')
                return
        else:
            self.stdout.write(f"Importing {len(data)} accident datasets")

        SectionAccidents.objects.all().delete()
        for row in data:
            data = {MAPPING[key]: row[key] for key in MAPPING}

            try:
                SectionAccidents.objects.create(**data)
            except IntegrityError as e:
                self.stderr.write("Error during import:")
                self.stderr.write(str(e))
                self.stderr.write(f"CSV: {json.dumps(row)}")
