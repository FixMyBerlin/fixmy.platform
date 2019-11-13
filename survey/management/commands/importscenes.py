from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from itertools import islice
from survey.models import Scene
import argparse
import csv
import sys


class Command(BaseCommand):
    help = 'Imports scenes'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            default=sys.stdin,
            help='A CSV file'
        )
        parser.add_argument(
            '--image-dir',
            type=str,
            default='KatasterKI/scenes',
            help='The directory of the scene images'
        )

    def handle(self, *args, **options):
        Scene.objects.all().delete()
        fieldnames = ['SceneID', 'Weight']
        reader = csv.DictReader(options['file'], fieldnames)

        for row in islice(reader, 1, None):
            try:
                parts = row['SceneID'].split('_')
                Scene.objects.create(
                    experiment=parts[1],
                    image='{}/{}.jpg'.format(
                        options['image_dir'], row['SceneID']),
                    number=parts[3],
                    perspective=parts[2],
                    project=parts[0],
                    weight=row['Weight']
                )
            except IntegrityError:
                pass
