import argparse
import csv
import logging
import psycopg2.errors
import sys

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fahrradparken.models import (
    ParkingFacility,
    ParkingFacilityCondition,
    ParkingFacilityOccupancy,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import parking facility dataset from S3 storage'
    fields = [
        'station_id',
        'external_id',
        'capacity',
        'stands',
        'covered',
        'two_tier',
        'secured',
        'parking_garage',
        'type',
        'source',
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=argparse.FileType('r'), default=sys.stdin, help='A CSV file'
        )

    def import_from_reader(self, reader):
        """Import data"""
        for row in reader:
            condition = row.get('condition')
            occupancy = row.get('occupancy')
            coordinates = row.get('location', '').split(',')
            longitude = float(coordinates[1].strip())
            latitude = float(coordinates[0].strip())
            kwargs = {k: row[k] if row[k] != '' else None for k in self.fields}
            kwargs['location'] = Point(longitude, latitude)
            try:
                created = ParkingFacility.objects.create(**kwargs)
                if condition:
                    ParkingFacilityCondition.objects.create(
                        parking_facility=created, value=condition
                    )
                if occupancy:
                    ParkingFacilityOccupancy.objects.create(
                        parking_facility=created, value=occupancy
                    )
            except IntegrityError as e:
                if type(e.__cause__) == psycopg2.errors.ForeignKeyViolation:
                    logger.warning(
                        'Skipped importing parking facility for missing station '
                        f"{row['station_id']}"
                    )
                elif type(e.__cause__) == psycopg2.errors.UniqueViolation:
                    logger.warning(
                        'Skipped importing duplicate parking facility '
                        f"{row['external_id']} of station {row['station_id']}"
                    )
                else:
                    raise

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'], delimiter=';')
        self.import_from_reader(reader)
