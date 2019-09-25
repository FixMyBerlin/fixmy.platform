import os
import sys
import logging
from django.core import management
from django.core.management.base import BaseCommand

BUCKET_NAME = 'Data/'
FPATH_SECTIONS = '/tmp/planning_sections.shp'
FPATH_SECTION_DETAILS = '/tmp/planning_section_details.csv'

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    """Load current data from S3, overwriting current data.
    
    This command executes the commands 

    - createinitialrevisions
    - migrate
    - downloadfiles
    - importsections
    - importsectiondetails

    in this order. Command parameters are specified using the constants 
    defined at the top of this file. If one of the files does not exist in S3, an 
    appropriate warning is emitted before importing any data.
    """

    help = 'Load current sections and projects from S3, overwriting current data'

    def handle(self, *args, **kwargs):
        try:
            logging.info('Creating initial revisions...')
            management.call_command('createinitialrevisions')

            logging.info('Migrating database...')
            management.call_command('migrate')

            logging.info('Downloading from S3 bucket Data/...')
            management.call_command('downloadfiles', 'Data/')

            try:
                os.stat(FPATH_SECTIONS)
            except FileNotFoundError:
                logging.error(
                    (
                        'Sections were not downloaded to , '
                        f'{FPATH_SECTIONS} update canceled'
                    )
                )
                sys.exit()

            try:
                os.stat(FPATH_SECTION_DETAILS)
            except FileNotFoundError:
                logging.error(
                    (
                        'Section details were not downloaded to '
                        f'{FPATH_SECTION_DETAILS}, update canceled'
                    )
                )
                sys.exit()

            logging.info('Importing sections...')
            management.call_command('importsections', FPATH_SECTIONS)

            logging.info('Importing section details...')
            management.call_command('importsectiondetails', FPATH_SECTION_DETAILS)

        except Exception as e:
            logging.error('Failed importing updated dataset')
            raise e
