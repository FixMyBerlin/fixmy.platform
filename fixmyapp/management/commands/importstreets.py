from django.core.management.base import BaseCommand
from django.contrib.gis.utils import LayerMapping
from fixmyapp.models import Edge
import os

# Auto-generated `LayerMapping` dictionary for Edge model
kanten_mapping = {
    'objectid': 'OBJECTID',
    'gml_parent_id': 'gml_parent_id',
    'gml_id': 'gml_id',
    'spatial_geometry': 'spatial_geometry',
    'spatial_name': 'spatial_name',
    'spatial_name_xsi_nil': 'spatial_name_xsi_nil',
    'spatial_alias': 'spatial_alias',
    'spatial_alias_xsi_nil': 'spatial_alias_xsi_nil',
    'spatial_type': 'spatial_type',
    'spatial_type_xsi_nil': 'spatial_type_xsi_nil',
    'elem_nr': 'ELEM_NR',
    'elem_nr_xsi_nil': 'ELEM_NR_xsi_nil',
    'strschl': 'STRSCHL',
    'strschl_xsi_nil': 'STRSCHL_xsi_nil',
    'str_name': 'STR_NAME',
    'str_name_xsi_nil': 'STR_NAME_xsi_nil',
    'str_bez': 'STR_BEZ',
    'str_bez_xsi_nil': 'STR_BEZ_xsi_nil',
    'strklasse1': 'STRKLASSE1',
    'strklasse1_xsi_nil': 'STRKLASSE1_xsi_nil',
    'strklasse': 'STRKLASSE',
    'strklasse_xsi_nil': 'STRKLASSE_xsi_nil',
    'strklasse2': 'STRKLASSE2',
    'strklasse2_xsi_nil': 'STRKLASSE2_xsi_nil',
    'vricht': 'VRICHT',
    'vricht_xsi_nil': 'VRICHT_xsi_nil',
    'bezirk': 'BEZIRK',
    'bezirk_xsi_nil': 'BEZIRK_xsi_nil',
    'stadtteil': 'STADTTEIL',
    'stadtteil_xsi_nil': 'STADTTEIL_xsi_nil',
    'ebene': 'EBENE',
    'ebene_xsi_nil': 'EBENE_xsi_nil',
    'von_vp': 'VON_VP',
    'von_vp_xsi_nil': 'VON_VP_xsi_nil',
    'bis_vp': 'BIS_VP',
    'bis_vp_xsi_nil': 'BIS_VP_xsi_nil',
    'laenge': 'LAENGE',
    'laenge_xsi_nil': 'LAENGE_xsi_nil',
    'gilt_von': 'GILT_VON',
    'gilt_von_xsi_nil': 'GILT_VON_xsi_nil',
    'okstra_id': 'OKSTRA_ID',
    'okstra_id_xsi_nil': 'OKSTRA_ID_xsi_nil',
    'geom': 'MULTILINESTRING',
}


class Command(BaseCommand):
    help = 'Imports street data from ...'

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
            kanten_mapping,
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
