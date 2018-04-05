from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import Edge
import os

# Auto-generated `LayerMapping` dictionary for Edge model
edge_mapping = {
    'objectid': 'OBJECTID',
    'gml_parent_id': 'gml_parent_id',
    'gml_id': 'gml_id',
    'spatial_geometry': 'spatial_geometry',
    'spatial_name': 'spatial_name',
    'spatial_alias': 'spatial_alias',
    'spatial_type': 'spatial_type',
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
    help = 'Imports edge data from ...'

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
            transform=False,
            encoding='utf-8'
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True
        )
