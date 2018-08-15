from django.core.management import BaseCommand
from django.conf import settings
import argparse
import boto3
import requests
import time


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=argparse.FileType('rb'), help='A GeoJSON file')
        parser.add_argument(
            '--show-progress',
            action='store_true',
            dest='progress',
            help='display upload progress any verbosity level.'
        )

    def handle(self, **options):
        credentials = self._retrieve_s3_credentials()
        client = self._create_s3_client(credentials)
        client.upload_fileobj(
            options['file'], credentials['bucket'], credentials['key'])
        upload = self._create_upload(credentials['url'])

        if options['progress'] or options['verbosity'] > 1:
            self.stdout.write('Uploading tileset {} to Mapbox').format(
                settings.MAPBOX_UPLOAD_TILESET)

            progress = upload['progress']

            while progress != 1:
                progress = self._upload_progress(upload['id'])
                self.stdout.write('{} %'.format(int(progress * 100)))
                time.sleep(1)

            self.stdout.write('Done')

    def _retrieve_s3_credentials(self):
        url = '{}/{}/credentials?access_token={}'.format(
            settings.MAPBOX_UPLOAD_URL,
            settings.MAPBOX_USERNAME,
            settings.MAPBOX_ACCESS_TOKEN
        )
        response = requests.post(url)
        return response.json()

    def _create_s3_client(self, credentials):
        session = boto3.session.Session(
            aws_access_key_id=credentials['accessKeyId'],
            aws_secret_access_key=credentials['secretAccessKey'],
            aws_session_token=credentials['sessionToken'],
            region_name=settings.MAPBOX_UPLOAD_REGION)
        return session.client('s3')

    def _create_upload(self, bucket_url):
        url = '{}/{}?access_token={}'.format(
            settings.MAPBOX_UPLOAD_URL,
            settings.MAPBOX_USERNAME,
            settings.MAPBOX_ACCESS_TOKEN
        )
        payload = {
            'tileset': settings.MAPBOX_UPLOAD_TILESET,
            'url': bucket_url,
            'name': settings.MAPBOX_UPLOAD_NAME
        }
        response = requests.post(url, json=payload)
        return response.json()

    def _upload_progress(self, upload_id):
        url = '{}/{}/{}?access_token={}'.format(
            settings.MAPBOX_UPLOAD_URL,
            settings.MAPBOX_USERNAME,
            upload_id,
            settings.MAPBOX_ACCESS_TOKEN
        )
        response = requests.get(url)
        return response.json()['progress']
