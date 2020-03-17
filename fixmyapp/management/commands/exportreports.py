from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from fixmyapp.models import Report, BikeStands
import argparse
import csv
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export published reports as CSV files'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            type=argparse.FileType('w', encoding='UTF-8'),
            help='name of the CSV file',
        )

    def handle(self, *args, **options):
        FIELDNAMES = [
            'id',
            'address',
            'description',
            'Anzahl gewünscht',
            'likes',
            'status',
            'status_reason',
            'Position',
        ]
        FIELDNAMES_DE = [_(entry) for entry in FIELDNAMES]

        csv_writer = csv.DictWriter(
            options['filename'], fieldnames=FIELDNAMES, dialect='excel'
        )

        # Write table headers using German translation
        csv_writer.writerow(dict(zip(FIELDNAMES, FIELDNAMES_DE)))

        for report in Report.objects.order_by('id').prefetch_related(
            'likes', 'bikestands'
        ):
            row_data = model_to_dict(report, fields=FIELDNAMES)
            row_data["Position"] = f"{report.geometry.y},{report.geometry.x}"

            bike_stands = BikeStands.objects.filter(report_ptr=report)
            if len(bike_stands) > 0:
                row_data['Anzahl gewünscht'] = bike_stands[0].number

            csv_writer.writerow(row_data)
