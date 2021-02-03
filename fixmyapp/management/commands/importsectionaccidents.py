from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.models import SectionAccidents
import argparse
import csv
import sys


# CSV col name -> model field name
MAPPING = {
    'section_id': 'section_id',
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

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'])

        prompt = f'Delete all accident data sets and import {len(list(reader))} new data sets?'
        if input(prompt) != '':
            self.stdout.write('Import cancelled')
            return

        SectionAccidents.objects.all().delete()
        for row in reader:
            data = {mapping[key]: row[key] for key in mapping}

            try:
                obj, _ = SectionAccidents.object.create(data)
            except IntegrityError as e:
                self.stderr.write(
                    f"Referenced section {row.get('section_id')} does not exist"
                )
