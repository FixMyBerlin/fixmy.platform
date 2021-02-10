import argparse
import csv
import json
import logging
import sys

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.management.csv_tools import MissingFieldError, validate_reader
from fixmyapp.models import SectionAccidents
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

logger = logging.getLogger(__name__)

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

    def user_confirm_import(self, data, skip_confirmation=False):
        """Ask user to confirm potentially destructive action."""
        prompt = f'Delete existing data and import {len(data)} new data sets?'
        if skip_confirmation is False:
            if input(prompt) != '':
                logger.info('Import cancelled')
                sys.exit(0)
        else:
            logger.info(f"Importing {len(data)} datasets")

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'])

        try:
            data = list(reader)
        except UnicodeDecodeError:
            logger.exception('')
            self.stderr.write(f"Error reading {options['file']} using UTF-8 codec.")
            sys.exit(1)

        try:
            validate_reader(reader, MAPPING)
        except MissingFieldError as err:
            logger.error(err)
            sys.exit(1)

        self.user_confirm_import(data, skip_confirmation=options['skip_confirmation'])

        SectionAccidents.objects.all().delete()
        for row in data:
            data = {MAPPING[key]: row[key] for key in MAPPING}

            try:
                SectionAccidents.objects.create(**data)
            except IntegrityError as e:
                # Django stores the original db-level exception on `__cause__`
                # when wrapping it in a Django error type
                if type(e.__cause__) == ForeignKeyViolation:
                    logger.warning(
                        f"Skipped importing section accidents for missing section {row['section_id']}"
                    )
                elif type(e.__cause__) == UniqueViolation:
                    logger.warning(
                        "Skipped importing duplicate section accidents for side "
                        f"{row['side']} of section {row['section_id']}"
                    )
                else:
                    raise
