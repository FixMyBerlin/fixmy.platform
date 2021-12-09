import tempfile
from django.core.management import call_command
from django.test import TestCase

from fahrradparken.models import ParkingFacility, Station

STATIONS_SAMPLE_PATH = 'fahrradparken/sample_data/stations-v1.0.geojson'
PARKING_FACILITIES_SAMPLE_PATH = 'fahrradparken/sample_data/parking_facilities.csv'


class StationImportTest(TestCase):
    def test_import_valid_data(self):
        """Test importing a valid station dataset."""
        call_command('importstations', STATIONS_SAMPLE_PATH)
        self.assertEqual(Station.objects.count(), 1)


class ParkingFacilityImportTest(TestCase):
    fixtures = ['station']

    def test_import_without_skip_list(self):
        call_command('importparkingfacilities', PARKING_FACILITIES_SAMPLE_PATH)
        self.assertEqual(ParkingFacility.objects.count(), 4)

    def test_import_with_skip_list(self):
        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.txt'
        ) as f:
            f.write("""1""")
            f.seek(0)
            call_command(
                'importparkingfacilities',
                PARKING_FACILITIES_SAMPLE_PATH,
                skip_stations=f,
            )
        self.assertEqual(ParkingFacility.objects.count(), 2)
