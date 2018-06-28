from django.core.files.storage import default_storage
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Download contents of storage bucket to /tmp'

    def add_arguments(self, parser):
        parser.add_argument(
            'dir',
            type=str,
            help='A directory in the bucket'
        )

    def handle(self, *args, **options):
        if not options['dir'].endswith('/'):
            directory = options['dir'] + '/'
        else:
            directory = options['dir']

        if not default_storage.exists(directory):
            raise CommandError(
                'The directory {} does not exist in bucket.'.format(directory)
            )

        files = default_storage.listdir(directory)[1]

        if len([f for f in files if f != '']) == 0:
            raise CommandError('The directory {} is empty'.format(directory))

        for file in (f for f in files if f != ''):
            target = '/tmp/' + file
            key = options['dir'] + file
            default_storage.bucket.download_file(key, target)
            self.stdout.write(
                'Successfully downloaded "{}" to "{}".'.format(key, target))

        self.stdout.write('Finished downloading files from bucket.')
