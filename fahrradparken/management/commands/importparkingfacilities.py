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
        parser.add_argument(
            '--delimiter',
            type=str,
            default=';',
            help='CSV file delimiter , or ;',
        )
        parser.add_argument(
            '--skip-stations', type=argparse.FileType('r'),
            help='A file containing a list of stations to skip'
        )

    def import_from_reader(self, reader, skip_stations):
        for row in reader:
            condition = row.get('condition')
            occupancy = row.get('occupancy')
            coordinates = row.get('location', '').split(', ')

            if len(coordinates) != 2:
                logger.warning(
                    f"Skipped importing parking facility {row['external_id']} due to malformed or missing coordinates"
                )
                continue

            longitude = float(coordinates[1].strip().replace(',', '.'))
            latitude = float(coordinates[0].strip().replace(',', '.'))
            kwargs = {k: row[k] if row[k] != '' else None for k in self.fields}
            kwargs['location'] = Point(longitude, latitude)
            kwargs['station_id'] = kwargs['external_id'].split('.')[0]
            if int(kwargs['station_id']) in skip_stations:
                logger.info(
                    f"Skipped importing parking facility {kwargs['external_id']} due to skip station list"
                )
                continue
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
                        f"{kwargs['station_id']}"
                    )
                elif type(e.__cause__) == psycopg2.errors.UniqueViolation:
                    logger.warning(
                        'Skipped importing duplicate parking facility '
                        f"{row['external_id']}"
                    )
                else:
                    raise

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'], delimiter=options['delimiter'])
        if options['skip_stations']:
            skip_stations = [int(s.rstrip()) for s in options['skip_stations'].readlines()]
        else:
            skip_stations = []
        self.import_from_reader(reader, skip_stations)
