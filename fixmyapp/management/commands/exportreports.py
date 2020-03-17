from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from fixmyapp.models import Report
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
            'likes',
            'status',
            'status_reason',
        ]
        FIELDNAMES_DE = [_(entry) for entry in FIELDNAMES]

        filters = {'published': True}

        csv_writer = csv.DictWriter(
            options['filename'], fieldnames=FIELDNAMES, dialect='excel'
        )

        # Write table headers using German translation
        csv_writer.writerow(dict(zip(FIELDNAMES, FIELDNAMES_DE)))

        for r in Report.objects.filter(**filters).order_by('id'):
            csv_writer.writerow(model_to_dict(r, fields=FIELDNAMES))
