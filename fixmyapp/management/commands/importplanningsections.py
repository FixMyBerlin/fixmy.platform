from django.core.management.base import BaseCommand

from fixmyapp.importing import import_planning_sections
import argparse
import sys


class Command(BaseCommand):
    help = 'Imports planning sections'

    def add_arguments(self, parser):
        parser.add_argument(
            'file',
            type=argparse.FileType('r'),
            default=sys.stdin,
            help='A CSV file'
        )
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display the progress bar in any verbosity level.'
        )

    def handle(self, *args, **options):
        import_planning_sections(options['file'])

