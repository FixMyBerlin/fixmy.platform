from django.db import transaction
from django.core.management.base import BaseCommand
from django.contrib.gis.utils.layermapping import LayerMapError
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import Section
import os

# The `category` field is not read beacuse it's formatted as a roman numeral,
# which LayerMapping can not read. If we want to use a street's actual category
# we need to work around that.

mapping = {
    'id': 'id',
    'street_name': 'name',
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
        parser.add_argument(
            '--delete',
            action='store_true',
            help='delete all existing sections before import',
        )

    def handle(self, *args, **options):

        try:
            with transaction.atomic():
                if options['delete'] is True:
                    Section.objects.all().delete()
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
