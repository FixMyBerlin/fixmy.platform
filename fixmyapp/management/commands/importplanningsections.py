from django.core.management.base import BaseCommand
from fixmyapp.models import Edge, PlanningSection
import argparse
import csv
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

    def handle(self, *args, **options):
        reader = csv.DictReader(options['file'])
        for row in reader:
            obj, created = PlanningSection.objects.get_or_create(
                pk=row['MetaID']
            )
            obj.name = row['Straßen Name']
            try:
                obj.edges.add(Edge.objects.get(pk=row['ElemNr']))
            except Edge.DoesNotExist as e:
                message = 'Referenced edge with ElemNr {} does not exist.'.format(row['ElemNr'])
                self.stderr.write(message)
            obj.geom_hash = obj.compute_geom_hash()
            obj.save()
