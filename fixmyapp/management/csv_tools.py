import logging
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fixmyapp.models import Photo, SectionDetails
import argparse
import csv
import sys

logger = logging.getLogger(__name__)


class MissingFieldError(Exception):
    """A required field is missing in a CSV file."""

    pass


def validate_reader(self, csv_reader, mapping):
    """Check that all required fields are contained in the csv file.

    Parameters:
        csv_reader (csv.DictReader): Reader configured with the input file
        mapping (dict): A dictionary mapping csv col names to model field names

    Raises:
        MissingFieldError: if a missing field is encountered
    """
    missing_fields = [
        field for field in mapping.keys() if field not in csv_reader.fieldnames
    ]
    if len(missing_fields) > 0:
        raise MissingFieldError(
            f"Input file is missing column: {', '.join(missing_fields)}"
        )