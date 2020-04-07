from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import BikeStands
import os

mapping = {
    'address': 'address',
    'created_date': 'created',
    'description': 'description',
    'geometry': 'POINT',
    'id': 'id',
    'number': 'number',
    'status_reason': 'status_reason',
    'status': 'status',
    'subject': 'subject',
}


class Command(BaseCommand):
    help = 'Imports reports from shape file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=str,
            help='A shape file - please see README.md for expected format',
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.',
        )

    def handle(self, *args, **options):
        lm = LayerMapping(
            BikeStands,
            os.path.abspath(options['file']),
            mapping,
            transform=True,
            encoding='utf-8',
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True,
        )
