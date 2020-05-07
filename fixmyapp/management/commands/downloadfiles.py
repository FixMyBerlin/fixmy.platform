from django.core.files.storage import default_storage
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Download contents of storage bucket to /tmp'

    def add_arguments(self, parser):
        parser.add_argument('dir', type=str, help='A directory in the bucket')

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

        valid_files = [f for f in files if f != '' and f != '.']

        if len(valid_files) == 0:
            raise CommandError('The directory {} is empty'.format(directory))

        for file in valid_files:
            target = '/tmp/' + file
            key = directory + file
            default_storage.bucket.download_file(key, target)
            if options['verbosity'] > 1:
                self.stdout.write(
                    'Successfully downloaded "{}" to "{}".'.format(key, target)
                )

        if options['verbosity'] > 0:
            self.stdout.write('Finished downloading files from bucket.')
