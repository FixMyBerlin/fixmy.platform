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
    'description',
    'status_reason',
    'number',
]

STATUS_CHOICES = [x[0] for x in BikeStands.STATUS_CHOICES]


class IntegrityError(ValueError):
    """Raised when imported data has errors that prevent importing it"""

    pass


def validate_entry(row, errorfn):
    """Validate a row of data representing an entry

    Doesn't validate linked origin reports"""

    assert float(row.get('long')) > 0
    assert float(row.get('lat')) > 0

    if ',' in row['origin_ids']:
        errorfn.append(
            ' has origin_ids separated by comma. Must be separated by semicolon.'
        )

    if row['status'] not in STATUS_CHOICES:
        errorfn(
            f"has invalid status {row['status']}. Valid values are {', '.join(STATUS_CHOICES)}"
        )


def process_origin(entry, origin_entry_id, errorfn, fix_status=False):
    """Add a given report id as an origin to a given planning entry"""
    try:
        origin_entry = BikeStands.objects.get(pk=origin_entry_id)
    except BikeStands.DoesNotExist:
        errorfn(
            f'links origin id {origin_entry_id:0>3} which does not exist in the database'
        )
        raise IntegrityError
    except ValueError:
        errorfn(f'has invalid origin id ({str(origin_entry_id)})')
        raise IntegrityError

    if origin_entry.status != BikeStands.STATUS_REPORT_ACCEPTED:
        if fix_status:
            origin_entry.status = BikeStands.STATUS_REPORT_ACCEPTED
            origin_entry.save()
        else:
            errorfn(
                f"links origin id {origin_entry_id:0>3}, which has the invalid status {origin_entry.status}"
            )

    if entry.geometry == origin_entry.geometry:
        if fix_status is False:
            errorfn(
                f"is in the same location as its origin report {origin_entry_id:0>3}"
            )

    entry.origin.add(origin_entry)


def process_entry(row, rowerror, force_insert=False):
    """Create or update an entry corresponding to a given row.

    New entries are created when `row` contains no value in the `id` key. If the
    `force_insert` parameter is set, a new entry is created if `id` contains a
    value but no corresponding entry to update is found in the local db. In this
    case, the new entry is created with the given id."""
    entry = None
    entry_id = None
    geometry = Point(float(row.get('long')), float(row.get('lat')))
    is_update = row.get("id") not in [None, ""]

    if is_update:
        entry_id = int(row.get("id"))
        try:
            entry = BikeStands.objects.get(pk=entry_id)
        except BikeStands.DoesNotExist:
            if force_insert:
                is_update = False
            else:
                rowerror(
                    f"specifies entry ID to update but entry {entry_id:03} not found in database"
                )
                raise IntegrityError

    if is_update:
        entry.address = row['address']
        entry.geometry = geometry
        entry.description = row['description']
        entry.status = row['status']
        entry.status_reason = row['status_reason']
        entry.number = int(row['number'])
    else:
        entry = BikeStands(
            address=row['address'],
            geometry=geometry,
            description=row['description'],
            status=row['status'],
            status_reason=row['status_reason'],
            number=row['number'],
            subject=Report.SUBJECT_BIKE_STANDS,
        )
        if force_insert and entry_id is not None:
            self.stdout.write(f"Set id {entry_id} on row {i}\n")
            entry.id = entry_id
    return entry


def create_report_plannings(rows, force_insert=False):
    """Create and update reports given an iterable of data objects"""
    entries = []
    errors = []
    for i, row in enumerate(rows):

        def rowerror(msg):
            errors.append(f"Row {(i+1):03} {msg}")

        validate_entry(row, rowerror)
        try:
            entry = process_entry(row, rowerror, force_insert=force_insert)
        except IntegrityError:
            continue
        entry.save()
        entries.append(entry)

        # Save back newly created entry ids on the row so that
        # `link_report_origins` can access them
        if row.get('id') in [None, ""]:
            row['id'] = entry.id

    if len(errors) > 0:
        sys.stderr.write(
            f"The import was aborted because of errors in the input data\n\n - "
        )
        formattederrors = "\n - ".join(sorted(errors))
        sys.stderr.write(formattederrors)
        sys.stderr.write("\n")
        raise IntegrityError
    return entries


def link_report_origins(entry_rows, fix_status=False):
    """Update existing entries with origin information from an iterable of entries"""
    errors = []

    for i, row in enumerate(entry_rows):

        def rowerror(msg):
            # +1 because of 0-indexing and +1 because of the header row
            errors.append(f"Row {(i+2):03} {msg}")

        entry_id = int(row.get("id"))
        entry = BikeStands.objects.get(pk=entry_id)

        linked_entries = row['origin_ids'].split(';')
        prev_linked_entries = entry.origin.all()
        for linked_entry in prev_linked_entries:
            if linked_entry.id not in linked_entries:
                entry.origin.remove(linked_entry)
        for origin_entry_id in linked_entries:
            if origin_entry_id == '':
                continue

            if origin_entry_id not in prev_linked_entries:
                try:
                    process_origin(
                        entry, origin_entry_id, rowerror, fix_status=fix_status
                    )
                except IntegrityError:
                    continue

    if len(errors) > 0:
        sys.stderr.write(
            f"Linking origin entries was aborted because of errors in the input data\n\n - "
        )
        formattederrors = "\n - ".join(sorted(errors))
        sys.stderr.write(formattederrors)
        sys.stderr.write("\n")
        raise IntegrityError


class Command(BaseCommand):
    help = '''Update and create bike stand reports and plannings from a CSV file.
    Entries are inserted when no id is defined in the input file and updated
    when an id is specified and found in the database.'''

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=str, help='CSV file with one planning per line'
        )
        parser.add_argument(
            '--fix-status',
            action='store_true',
            dest='fix_status',
            help='update origin report status to report_accepted',
        )
        parser.add_argument(
            '--force-insert',
            action='store_true',
            dest='force_insert',
            help='create new entries when ID to update is specified but not found in database',
        )

    def read_input(self, fname):
        """Read a csv file, checking for file format"""

        with open(fname) as f:
            csv_reader = csv.DictReader(f, delimiter=',')
            rows = [row for row in csv_reader]

        for col in REQUIRED_COLS:
            assert (
                col in csv_reader.fieldnames
            ), f'The input file is missing the {col} column'

        errmsg = 'Input file may not have both geometry and lon, lat columns'
        if "geometry" in csv_reader.fieldnames:
            assert "long" not in csv_reader.fieldnames, errmsg
            assert "lat" not in csv_reader.fieldnames, errmsg
        elif "long" in csv_reader.fieldnames:
            assert "geometry" not in csv_reader.fieldnames, errmsg
        elif "lat" in csv_reader.fieldnames:
            assert "geometry" not in csv_reader.fieldnames, errmsg
        else:
            raise IntegrityError(
                'The input file is missing entry locations defined \
                in either a "geometry" column or in "long" and "lat" columns.'
            )
        return rows

    def handle(self, *args, **kwargs):
        try:
            entry_rows = self.read_input(kwargs['file'])
        except:
            self.stderr.write("There was an error reading the input file")
            raise

        try:
            with transaction.atomic():
                entries = create_report_plannings(
                    entry_rows, force_insert=kwargs['force_insert']
                )
                link_report_origins(entry_rows, fix_status=kwargs['fix_status'])
                self.stdout.write(f"Created or updated {len(entries)} plannings\n")
        except IntegrityError:
            self.stderr.write(
                f"There were errors during import. No plannings created or modified."
            )
            sys.exit(1)
