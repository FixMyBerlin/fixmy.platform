from django.core.management.base import BaseCommand
from fixmyapp.models import Section
import argparse
import json


class Command(BaseCommand):
    help = 'Exports planning sections as GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('w'),
            help='write to file'
        )
        parser.add_argument(
            '--indent',
            type=int,
            default=None,
            help='indentation level for pretty printing'
        )

    def handle(self, *args, **options):
        result = {
            'type': 'FeatureCollection',
            'features': []
        }

        for s in Section.objects.all():
            feature = {
                'type': 'Feature',
                'geometry': json.loads(s.geometry.json),
                'properties': {
                    'id': s.pk,
                    'street_name': s.street_name,
                    'suffix': s.suffix,
                    'borough': s.borough,
                    'street_category': s.street_category,
                    'velocity': float(round(s.velocity_index(), 3)),
                    'safety': float(round(s.safety_index(), 3))
                }
            }

            for detail in s.details.all():
                orientation = detail.orientation
                velocity = float(round(detail.velocity_index(), 3))
                safety = float(round(detail.safety_index(), 3))
                
                prefix = 'side{}_'.format(detail.side)
                feature['properties'][prefix + 'orientation'] = orientation
                feature['properties'][prefix + 'velocity'] = velocity
                feature['properties'][prefix + 'safety'] = safety

            result['features'].append(feature)

        json.dump(result, options['file'], indent=options['indent'])
