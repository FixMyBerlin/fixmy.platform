from django.core.management.base import BaseCommand
from fixmyapp.models import Section
import argparse
import json


class Command(BaseCommand):
    help = 'Exports planning sections as GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('w'), help='write to file')
        parser.add_argument(
            '--indent',
            type=int,
            default=2,
            help='indentation level for pretty printing',
        )

    def handle(self, *args, **options):
        result = {'type': 'FeatureCollection', 'features': []}

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
                    'is_road': s.is_road,
                },
            }

            # the HBI methods are not configured to handle the fake data that
            # we have for intersections at the moment, so these fields are only
            # populated when `section.is_road`

            if s.is_road is True:
                feature['properties']['velocity'] = float(round(s.velocity_index(), 3))
                feature['properties']['safety'] = float(round(s.safety_index(), 3))

                for detail in s.details.all():
                    orientation = detail.orientation
                    velocity = float(round(detail.velocity_index(), 3))
                    safety = float(round(detail.safety_index(), 3))

                    prefix = 'side{}_'.format(detail.side)
                    feature['properties'][prefix + 'orientation'] = orientation
                    feature['properties'][prefix + 'velocity'] = velocity
                    feature['properties'][prefix + 'safety'] = safety

            for entry in s.accidents.all():
                feature['properties'][f'side{entry.side}_killed'] = entry.killed
                feature['properties'][
                    f'side{entry.side}_severely_injured'
                ] = entry.severely_injured
                feature['properties'][
                    f'side{entry.side}_slightly_injured'
                ] = entry.slightly_injured
                feature['properties'][f'side{entry.side}_source'] = entry.source
                feature['properties'][f'side{entry.side}_risk_level'] = entry.risk_level

            result['features'].append(feature)

        json.dump(result, options['file'], indent=options['indent'], ensure_ascii=False)
