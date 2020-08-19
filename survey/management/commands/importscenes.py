from django.core.management.base import BaseCommand
from itertools import islice
from survey.models import Scene
import argparse
import csv
import sys


class Command(BaseCommand):
    help = 'Imports scenes'

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=argparse.FileType('r'), default=sys.stdin, help='A CSV file'
        )
        parser.add_argument(
            '--image-dir',
            type=str,
            default='KatasterKI/scenes',
            help='The directory of the scene images',
        )

    def handle(self, *args, **options):
        fieldnames = ['SceneID', 'Weight']
        reader = csv.DictReader(options['file'], fieldnames)

        for row in islice(reader, 1, None):
            parts = row['SceneID'].split('_')
            scene, _ = Scene.objects.update_or_create(
                defaults={
                    'weight': row['Weight'],
                    'image': '{}/{}.jpg'.format(options['image_dir'], row['SceneID']),
                },
                project=parts[0],
                experiment=parts[1],
                perspective=parts[2],
                number=parts[3],
            )
