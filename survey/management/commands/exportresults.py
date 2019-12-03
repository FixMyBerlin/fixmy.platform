import argparse
import json
import sys
from django.db.models import Prefetch
from django.core.management.base import BaseCommand
from survey.models import Rating, Session
from survey.serializers import SessionSerializer


class Command(BaseCommand):
    help = 'Export results to a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            'project', type=int, default=1, help='Survey project to export'
        )
        parser.add_argument(
            'file',
            type=argparse.FileType('w'),
            default=sys.stdout,
            help='Target path for result contents',
        )

    def handle(self, *args, **options):
        prefetch_ratings = Prefetch('ratings', queryset=Rating.objects.order_by('id'))
        queryset = Session.objects.filter(project=options['project']).prefetch_related(
            prefetch_ratings
        )
        data = SessionSerializer(queryset, many=True).data

        json.dump(data, options['file'], indent=2, ensure_ascii=False)
