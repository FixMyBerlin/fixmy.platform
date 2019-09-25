from django.core.management.base import BaseCommand
from fixmyapp.models import Project
import argparse
import json


class Command(BaseCommand):
    help = 'Exports projects as GeoJSON'

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

        filters = {
            'geometry__isnull': False,
            'published': True
        }

        for p in Project.objects.filter(**filters):
            result['features'].append({
                'type': 'Feature',
                'geometry': json.loads(p.geometry.json),
                'properties': {
                    'id': p.pk,
                    'title': p.title,
                    'side': p.side,
                    'responsible': p.responsible,
                    'short_description': p.short_description,
                    'category': p.category,
                    'project_key': p.project_key,
                    'street_name': p.street_name,
                    'borough': p.borough,
                    'costs': p.costs,
                    'draft_submitted': p.draft_submitted,
                    'construction_started': p.construction_started,
                    'construction_completed': p.construction_completed,
                    'phase': p.phase,
                    'status': p.status,
                    'external_url': p.external_url
                }
            })

        json.dump(result, options['file'], indent=options['indent'])
