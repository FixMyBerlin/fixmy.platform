import csv
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from reports.models import BikeStands

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


def load_reports(rows):
    new_reports = []
    for i, row in enumerate(rows):
        lon, lat = [float(x) for x in row['geometry'].split(',')]
        assert (
            row['status'] in STATUS_CHOICES
        ), f"Status '{row['status']}' of entry in row {i+1} is not a valid status. Possible values are {', '.join(STATUS_CHOICES)}.'"
        new_report = BikeStands(
            address=row['address'],
            geometry=Point(lon, lat),
            description=row['description'],
            status=row['status'],
            status_reason=row['status_reason'],
            number=row['number'],
        )

        assert (
            ',' not in row['origin_ids']
        ), f"Column origin_ids must contain semicolon-separated values. Found comma in line {i+1}."

        linked_entries = row['origin_ids'].split(';')
        for entry_id in linked_entries:
            entry = BikeStands.objects.get(ok=entry_id)
            assert (
                entry is not None
            ), f'Could not find report {entry_id} found in origin_ids of line {i+1}'
            new_report.origin.add(entry)
    return new_reports


class Command(BaseCommand):
    help = 'Import planned bike stand constructions from a csv file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=str, help='CSV file with one planning per line'
        )

    def handle(self, *args, **kwargs):
        fname = kwargs['file']

        with open(fname) as f:
            csv_reader = csv.DictReader(f, delimiter=',')
            rows = [row for row in csv_reader]

        for col in REQUIRED_COLS:
            assert (
                col in csv_reader.fieldnames
            ), f'The input file is missing the {col} column'

        reports = load_reports(rows)
        BikeStands.objects.bulk_create(reports)
