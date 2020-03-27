from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import BikeStands
import os

mapping = {
    'address': 'address',
    'subject': 'subject',
    'description': 'description',
    'number': 'number',
    'fee_acceptable': 'fee_acceptable',
    'geometry': 'POINT',
}


class Command(BaseCommand):
    help = (
        'Imports reports from shape file'
    )

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='A shape file - please see README.md for expected format')
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.'
        )

    def handle(self, *args, **options):
        lm = LayerMapping(
            BikeStands,
            os.path.abspath(options['file']),
            mapping,
            transform=True,
            encoding='utf-8'
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True
        )
