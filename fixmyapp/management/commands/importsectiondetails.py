import argparse
import csv
import logging
import sys

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.models import Photo, SectionDetails
from psycopg2.errors import ForeignKeyViolation

logger = logging.getLogger(__name__)

# Mapping CSV col name -> model field name
# the `exist` column is handled separately below
mapping = {
    'section_id': 'section_id',
    'side': 'side',
    'tempolimit': 'speed_limit',
    'dailytraffic': 'daily_traffic',
    'dailytraffic_heavy': 'daily_traffic_heavy',
    'daily_traffic_transporter': 'daily_traffic_cargo',
    'dailiy_traffic_bus': 'daily_traffic_bus',
    'length': 'length',
    'crossings': 'crossings',
    'orientation': 'orientation',
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


class MissingFieldError(Exception):
    pass


class Command(BaseCommand):
    help = 'Imports section details'

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=argparse.FileType('r'), default=sys.stdin, help='A CSV file'
        )

    def validate_reader(self, csv_reader):
        """Check that all required fields are contained in the csv file."""
        missing_fields = [
            field for field in mapping.keys() if field not in csv_reader.fieldnames
        ]
        if len(missing_fields) > 0:
            raise MissingFieldError(
                f"Input file is missing column: {', '.join(missing_fields)}"
            )
        return True

    def import_from_reader(self, reader):
        """Import data."""

        for row in (row for row in reader if row['exist'] == '1'):
            # Marshall CSV key names and formatting to Model format
            kwargs = {mapping[key]: row[key].replace(',', '.') for key in mapping}

            try:
                obj, created = SectionDetails.objects.update_or_create(**kwargs)
                for path in row['rva_pics'].split():
                    photo = Photo(
                        content_object=obj,
                        copyright='Geoportal Berlin / Radverkehrsanlagen',
                        src='rva_pics{}'.format(path),
                    )
                    photo.save()
            except IntegrityError as e:
                # Django stores the original db-level exception on `__cause__`
                # when wrapping it in a Django error type
                if type(e.__cause__) == ForeignKeyViolation:
                    logger.warning(
                        f"Skipped importing section details for missing section {row['section_id']}"
                    )
                else:
                    raise

    def handle(self, *args, **options):
        SectionDetails.objects.all().delete()
        reader = csv.DictReader(options['file'])

        try:
            self.validate_reader(reader)
        except MissingFieldError as err:
            logger.error(err)
            sys.exit(1)

        self.import_from_reader(reader)
