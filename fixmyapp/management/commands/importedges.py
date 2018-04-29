from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import Edge
import os

# Auto-generated `LayerMapping` dictionary for Edge model
edge_mapping = {
    'elem_nr': 'ELEM_NR',
    'strschl': 'STRSCHL',
    'str_name': 'STR_NAME',
    'str_bez': 'STR_BEZ',
    'strklasse1': 'STRKLASSE1',
    'strklasse': 'STRKLASSE',
    'strklasse2': 'STRKLASSE2',
    'vricht': 'VRICHT',
    'bezirk': 'BEZIRK',
    'stadtteil': 'STADTTEIL',
    'ebene': 'EBENE',
    'von_vp': 'VON_VP',
    'bis_vp': 'BIS_VP',
    'laenge': 'LAENGE',
    'gilt_von': 'GILT_VON',
    'okstra_id': 'OKSTRA_ID',
    'geom': 'MULTILINESTRING',
}


class Command(BaseCommand):
    help = 'Imports edges'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='A GeoJSON file')
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.'
        )

    def handle(self, *args, **options):
        lm = LayerMapping(
            Edge,
            os.path.abspath(options['file']),
            edge_mapping,
            transform=True,
            encoding='utf-8',
            unique=('elem_nr',)
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True
        )
