import csv
import sys
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction
from reports.models import BikeStands, Report

REQUIRED_COLS = [
    'origin_ids',
    'status',
    'address',
    'geometry',
    'description',
    'status_reason',
    'number',
]

STATUS_CHOICES = [x[0] for x in BikeStands.STATUS_CHOICES]


def create_report_plannings(rows):
    entries = []
    invalid_status = set()
    for i, row in enumerate(rows):
        assert len(row['geometry']) > 0, f"Geometry of line {i+1} is empty"
        lon, lat = [float(x) for x in row['geometry'].split(',')]

        assert (
            row['status'] in STATUS_CHOICES
        ), f"Status '{row['status']}' of entry in row {i+1} is not a valid status. Possible values are {', '.join(STATUS_CHOICES)}.'"

        assert (
            ',' not in row['origin_ids']
        ), f"Column origin_ids must contain semicolon-separated values. Found comma in line {i+1}."

        entry = BikeStands(
            address=row['address'],
            geometry=Point(lon, lat),
            description=row['description'],
            status=row['status'],
            status_reason=row['status_reason'],
            number=row['number'],
            subject=Report.SUBJECT_BIKE_STANDS,
        )
        entry.save()

        linked_entries = row['origin_ids'].split(';')
        if len(linked_entries) > 0 and len(row['origin_ids']) > 0:
            for origin_entry_id in linked_entries:
                try:
                    origin_entry = BikeStands.objects.get(pk=origin_entry_id)
                except BikeStands.DoesNotExist:
                    raise BikeStands.DoesNotExist(
                        f'Could not find report {origin_entry_id} found in origin_ids of line {i+1}'
                    )
                entry.origin.add(origin_entry)
                if entry.status != BikeStands.STATUS_REPORT_ACCEPTED:
                    invalid_status.add(origin_entry_id)
            entry.save()

            # Create notifications for authors of origin reports
            entry.enqueue_notifications()
        entries.append(entry)

    if len(invalid_status) > 0:
        sys.stdout.write(
            f"{len(invalid_status)} reports were linked to plannings despite not having the correct status 'report_accepted'\n"
        )

    return entries


class Command(BaseCommand):
    help = 'Import planned bike stand constructions from a csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=str, help='CSV file with one planning per line'
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        fname = kwargs['file']

        with open(fname) as f:
            csv_reader = csv.DictReader(f, delimiter=',')
            rows = [row for row in csv_reader]

        for col in REQUIRED_COLS:
            assert (
                col in csv_reader.fieldnames
            ), f'The input file is missing the {col} column'

        entries = create_report_plannings(rows)
        self.stdout.write(f"Created {len(entries)} plannings\n")
