import os
from django.contrib.gis.utils import LayerMapping
from .models import Edge

# Auto-generated `LayerMapping` dictionary for Edge model
edge_mapping = {
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


shp = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'data/Kanten', 'da2933e507454ad6a71135ee4122b471_1.geojson'),
)

def run(verbose=True):
    lm = LayerMapping(
        Edge, shp, edge_mapping,
        transform=False, encoding='utf-8',
    )
    lm.save(strict=True, verbose=verbose)
