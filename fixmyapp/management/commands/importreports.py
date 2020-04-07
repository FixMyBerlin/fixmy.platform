from django.contrib.gis.utils import LayerMapping
from django.core.management.base import BaseCommand
from fixmyapp.models import BikeStands
import os
import json

from . import LayerMapping as LayerMappingPatched

default_mapping = {
    'address': 'address',
    'created_date': 'created',
    'description': 'description',
    'geometry': 'POINT',
    'id': 'id',
    'number': 'number',
    'status_reason': 'status_reason',
    'status': 'status',
    'subject': 'subject',
}


class Command(BaseCommand):
    help = 'Imports reports from shape file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=str,
            help='A shape file - please see README.md for expected format',
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.',
        )

    def _create_mapping(self, filename, verbosity):
        """Guess available fields in source file by looking at first feature."""
        mapping = default_mapping

        if filename.endswith('json'):
            with open(filename) as f:
                data = json.load(f)
            try:
                available_fields = data["features"][0]["properties"].keys()
            except KeyError:
                self.stderr.write("Could not extract available fields from json file")
                available_fields = default_mapping.keys()
            else:
                if verbosity > 0:
                    self.stdout.write(
                        "Using fields available in source file: "
                        + ",".join(available_fields)
                    )
                mapping = {}
                for field in available_fields:
                    if field in default_mapping.keys():
                        mapping[field] = default_mapping[field]
                    elif verbosity > 0:
                        self.stdout.write("No mapping available for field " + field)

                mapping["geometry"] = default_mapping["geometry"]
        return mapping

    def handle(self, *args, **options):
        mapping = self._create_mapping(options['file'], options['verbosity'])

        if "id" in mapping.keys():
            UNIQUE_PARAM = ('id',)
            LayerMappingCls = LayerMappingPatched
        else:
            UNIQUE_PARAM = None
            LayerMappingCls = LayerMapping

        lm = LayerMappingCls(
            BikeStands,
            os.path.abspath(options['file']),
            mapping,
            transform=True,
            encoding='utf-8',
            unique=UNIQUE_PARAM,
        )
        lm.save(
            verbose=True if options['verbosity'] > 2 else False,
            progress=options['progress'] or options['verbosity'] > 1,
            silent=options['verbosity'] == 0,
            stream=self.stdout,
            strict=True,
        )
