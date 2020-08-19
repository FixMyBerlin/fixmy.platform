from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Value
from django.db.models.functions import Concat


def anonymize_user_data(preserve_staff):
    if preserve_staff:
        users = get_user_model().objects.filter(is_staff=False)
    else:
        users = get_user_model().objects

    users.update(
        email='', username=Concat(Value('user-'), 'id'), first_name='', last_name=''
    )


class Command(BaseCommand):
    help = 'Removes personal information from the data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--preserve-staff',
            action='store_true',
            default=False,
            dest='preserve-staff',
            help='preserve staff users',
        )

    def handle(self, *args, **options):
        anonymize_user_data(options['preserve-staff'])
