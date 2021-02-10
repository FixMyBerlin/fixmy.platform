from django.core.management.base import BaseCommand
from django.contrib.gis.utils.layermapping import LayerMapError
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import Section
import os

mapping = {
    'id': 'id',
    'street_name': 'name',
    'street_category': 'category',
    'suffix': 'suffix',
    'borough': 'borough',
    'geometry': 'MULTILINESTRING',
    'is_road': 'is_road',
}


class Command(BaseCommand):
    help = 'Imports sections'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='A shape file')
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.',
        )

    def handle(self, *args, **options):
        try:
            lm = LayerMapping(
                Section,
                os.path.abspath(options['file']),
                mapping,
                transform=True,
                encoding='utf-8',
                unique=('id',),
            )
        except LayerMapError as e:
            self.stderr.write(f"Error importing sections from {options['file']}: {e}")
            sys.exit(1)
        else:
            lm.save(
                verbose=True if options['verbosity'] > 2 else False,
                progress=options['progress'] or options['verbosity'] > 1,
                silent=options['verbosity'] == 0,
                stream=self.stdout,
                strict=True,
            )
