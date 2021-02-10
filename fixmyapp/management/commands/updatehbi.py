import os
import sys
import logging
from django.core import management
from django.core.management.base import BaseCommand

BUCKET_NAME = 'Data/'
FPATH_ROAD_SECTIONS = '/tmp/road_sections_v11.shp'
FPATH_INTERSECTIONS = '/tmp/intersections_v11.shp'
FPATH_SECTION_DETAILS = '/tmp/planning_section_details.csv'
FPATH_SECTION_ACCIDENTS = '/tmp/planning_section_accidents.csv'

logger = logging.getLogger('updatehbi')
logger.setLevel(logging.INFO)


class Command(BaseCommand):
    """Load current data for HBI from S3, overwriting current data.

    This command executes the commands

    - createinitialrevisions
    - migrate
    - downloadfiles
    - importsections
    - importsectiondetails
    - importsectionaccidents

    in this order. Command parameters are specified using the constants
    defined at the top of this file. If one of the files does not exist in S3, an
    appropriate warning is emitted before importing any data.
    """

    help = 'Load current sections and projects from S3, overwriting current data'

    def handle(self, *args, **kwargs):
        try:
            logger.info('Creating initial revisions...')
            management.call_command('createinitialrevisions')

            logger.info('Migrating database...')
            management.call_command('migrate')

            logger.info('Downloading from S3 bucket Data/...')
            management.call_command('downloadfiles', 'Data/')

            try:
                os.stat(FPATH_ROAD_SECTIONS)
            except FileNotFoundError:
                logger.error(
                    (
                        'Road sections were not downloaded to , '
                        f'{FPATH_ROAD_SECTIONS} update canceled'
                    )
                )
                sys.exit()

            try:
                os.stat(FPATH_INTERSECTIONS)
            except FileNotFoundError:
                logger.error(
                    (
                        'Intersections were not downloaded to , '
                        f'{FPATH_INTERSECTIONS} update canceled'
                    )
                )
                sys.exit()

            try:
                os.stat(FPATH_SECTION_DETAILS)
            except FileNotFoundError:
                logger.error(
                    (
                        'Section details were not downloaded to '
                        f'{FPATH_SECTION_DETAILS}, update canceled'
                    )
                )
                sys.exit()

            try:
                logger.info('Importing road sections...')
                management.call_command('importsections', FPATH_ROAD_SECTIONS)

                logger.info('Importing intersections...')
                management.call_command('importsections', FPATH_INTERSECTIONS)
            except Exception:
                self.stderr.write(
                    "Error importing sections, cannot proceed with update."
                )
                sys.exit(1)

            logger.info('Importing section details...')
            management.call_command('importsectiondetails', FPATH_SECTION_DETAILS)

            logger.info('Importing section accident dataset...')
            management.call_command('importsectionaccidents', FPATH_SECTION_ACCIDENTS)

        except Exception as e:
            logger.error('Failed importing updated dataset')
            raise e
        else:
            logger.info('Update finished')
