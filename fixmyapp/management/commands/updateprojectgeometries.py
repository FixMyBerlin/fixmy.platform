from django.contrib.gis.gdal import OGRGeometry
from django.core.management.base import BaseCommand
from fixmyapp.models import Project
import django.contrib.gis.utils
import os
import sys

from . import LayerMapping


class Command(BaseCommand):
    help = 'Update project geometries'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='A shape file')
        parser.add_argument(
            'type',
            choices=['multipoint', 'linestring'],
            help='The type of geometries in the shape file',
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.',
        )

    def handle(self, *args, **options):
        mapping = {'project_key': 'ProjectKey', 'geometry': options['type']}
        lm = LayerMapping(
            Project,
            os.path.abspath(options['file']),
            mapping,
            transform=True,
            encoding='utf-8',
            unique=('project_key',),
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=False,
        )
