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


@transaction.atomic
def create_report_plannings(rows, force=False):
    entries = []
    errors = []
    for i, row in enumerate(rows):

        def rowerror(msg):
            errors.append(f"Row {(i+1):03} {msg}")

        if len(row['geometry']) == 0:
            rowerror("has empty geometry field")
            continue

        lon, lat = [float(x) for x in row['geometry'].split(',')]

        if row['status'] not in STATUS_CHOICES:
            rowerror(
                f"has invalid status {row['status']}. Valid values are {', '.join(STATUS_CHOICES)}"
            )

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

        if ',' in row['origin_ids']:
            rowerror.append(
                ' has origin_ids separated by comma. Must be separated by semicolon.'
            )
            continue

        linked_entries = row['origin_ids'].split(';')
        if len(linked_entries) > 0 and len(row['origin_ids']) > 0:
            for origin_entry_id in linked_entries:
                try:
                    origin_entry = BikeStands.objects.get(pk=origin_entry_id)
                except BikeStands.DoesNotExist:
                    rowerror(
                        f'links origin id {origin_entry_id:0>3} which does not exist in the database'
                    )
                    continue

                if origin_entry.status != BikeStands.STATUS_REPORT_ACCEPTED:
                    rowerror(
                        f"links origin id {origin_entry_id:0>3}, which has the invalid status {origin_entry.status}"
                    )
                    if force:
                        origin_entry.status = BikeStands.STATUS_REPORT_ACCEPTED

                if entry.geometry == origin_entry.geometry:
                    rowerror(
                        f"is in the same location as its origin report {origin_entry_id:0>3}"
                    )

                entry.origin.add(origin_entry)
            entry.save()
        entries.append(entry)

    if len(errors) > 0:
        sys.stderr.write(
            f"The import was aborted because of errors in the input data\n\n - "
        )
        formattederrors = "\n - ".join(sorted(errors))
        sys.stderr.write(formattederrors)
        sys.stderr.write("\n")
        raise ValueError(f"There were errors during import:\n- {formattederrors}")
    return entries


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

        try:
            entries = create_report_plannings(rows)
            self.stdout.write(f"Created {len(entries)} plannings\n")
        except ValueError:
            self.stdout.write("There were errors during import. No plannings created.")
