from django.core.management import call_command
from django.test import TestCase

from fahrradparken.models import Station

STATIONS_SAMPLE_PATH = 'fahrradparken/sample_data/stations-v1.0.geojson'


class StationImportTest(TestCase):
    def test_import_valid_data(self):
        """Test importing a valid station dataset."""
        call_command('importstations', STATIONS_SAMPLE_PATH)
        self.assertEqual(Station.objects.count(), 1)
