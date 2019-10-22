from django.core.management.base import BaseCommand
from fixmyapp.models import Report
import argparse
import json


class Command(BaseCommand):
    help = 'Exports (new) reports without photos and author as GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('w'), help='write to file')
        parser.add_argument(
            '--indent',
            type=int,
            default=None,
            help='indentation level for pretty printing',
        )

    def handle(self, *args, **options):
        result = {'type': 'FeatureCollection', 'features': []}
        filters = {'status': Report.STATUS_NEW, 'geometry__isnull': False}

        for r in Report.objects.filter(**filters):
            result['features'].append(
                {
                    'type': 'Feature',
                    'geometry': json.loads(r.geometry.json),
                    'properties': {
                        'id': r.pk,
                        'address': r.address,
                        'description': r.description,
                        'details': r.details,
                        'likes': r.likes.count(),
                        'published': r.published,
                        'status': r.status,
                        'status_reason': r.status_reason,
                    },
                }
            )

        json.dump(result, options['file'], indent=options['indent'], ensure_ascii=False)
