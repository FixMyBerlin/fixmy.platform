from django.core.management.base import BaseCommand
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _
from django.utils.formats import date_format
from fixmyapp.models import PlaystreetSignup
import argparse
import csv

FIELDNAMES = {
    'street': 'Spielstraße',
    'captain': _('captain'),
    'first_name': _('first_name'),
    'last_name': _('last_name'),
    'email': _('email'),
    'message': _('message'),
    'created_date': 'Eingereicht',
    'tos_accepted': _('tos_accepted'),
    'id': _('Kennziffer'),
}


class Command(BaseCommand):
    help = 'Export signups for play streets'

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            type=argparse.FileType('w', encoding='UTF-8'),
            help='output filename',
        )

    def handle(self, *args, **options):
        query = PlaystreetSignup.objects.order_by('street', 'captain', 'last_name')

        csv_writer = csv.DictWriter(
            options['filename'], fieldnames=FIELDNAMES.keys(), dialect='excel'
        )

        # Write table headers using German translation
        csv_writer.writerow(FIELDNAMES)

        for report in query:
            row_data = model_to_dict(report, fields=FIELDNAMES.keys())
            row_data['created_date'] = date_format(
                report.created_date, format='DATETIME_FORMAT', use_l10n=True
            )
            row_data['tos_accepted'] = 'Ja' if report.tos_accepted else 'Nein'
            row_data['captain'] = 'Ja' if report.captain else 'Nein'

            csv_writer.writerow(row_data)
