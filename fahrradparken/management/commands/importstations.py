import json
import os

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.db import transaction

from fahrradparken.models import Station

# Mapping of dataset field values to model field values (see Station model)
TRAVELLER_COUNT_RANGES = {
    "unter 100": 1,
    "100-300": 2,
    "301-1000": 3,
    "1001-3000": 4,
    "3001-10000": 5,
    "10001-50000": 6,
    "über 50000": 7,
}


class Command(BaseCommand):
    help = 'Imports train station dataset'

    def add_arguments(self, parser):
        parser.add_argument(
            'file', type=str, help='A geojson file containing a station dataset'
        )

    def validate(self, feature):
        """Return true if a feature has all required properties."""
        if feature["geometry"]["type"] != 'Point':
            self.stderr.write(
                f"Stations may not have geometries other than POINT\n\n{json.dumps(feature)}"
            )
            return False

        REQUIRED_PROPERTIES = [
            "Bf-Nr",
            "Bahnhof",
            "Range Reisende pro Tag",
            "PLZ",
            "Gemeindename",
            "Produktlinie\n(Stand: 03.03.2021)",
            "VERKEHR: Kann folgende Werte annehmen 'FV' (mit Fernverkehr), 'RV' (nur Regionalverkehr) oder 'nur DPN' (nur Regionalverkehr von privaten Eisenbahnunternehmen).",
        ]

        has_missing_fields = not all(
            p in feature["properties"].keys() for p in REQUIRED_PROPERTIES
        )
        if has_missing_fields is True:
            self.stderr.write(
                f"Station has missing properties\n\n{json.dumps(feature)}"
            )
            return False

        return True

    def is_long_distance(self, feature):
        """Return true if this station is serving long distance lines."""
        value = feature["properties"].get(
            "VERKEHR: Kann folgende Werte annehmen 'FV' (mit Fernverkehr), 'RV' (nur Regionalverkehr) oder 'nur DPN' (nur Regionalverkehr von privaten Eisenbahnunternehmen)."
        )
        return isinstance(value, str) and 'FV' in value

    def is_light_rail(self, feature):
        """Return true if this station serves light trail trains."""
        return feature["properties"]["Produktlinie\n(Stand: 03.03.2021)"] == 'S-Bahnhof'

    def handle(self, *args, **kwargs):
        path = os.path.abspath(kwargs['file'])
        with open(path) as f:
            data = json.load(f)

        num_entries = len(data.get('features'))
        num_updates = 0

        with transaction.atomic():
            for i, feature in enumerate(data.get('features', [])):
                if i % 500 == 0:
                    self.stdout.write(f'Processed {i} / {num_entries} stations')

                if not self.validate(feature):
                    continue

                props = feature["properties"]
                instance = Station.objects.filter(id=int(props.get('Bf-Nr'))).first()

                travellers = TRAVELLER_COUNT_RANGES.get(
                    props.get('Range Reisende pro Tag'), 0
                )

                if instance is None:
                    instance = Station.objects.create(
                        id=props.get('Bf-Nr'),
                        name=props.get('Bahnhof'),
                        location=Point(feature["geometry"]["coordinates"]),
                        travellers=travellers,
                        post_code=props.get('PLZ'),
                        is_long_distance=self.is_long_distance(feature),
                        is_light_rail=self.is_light_rail(feature),
                        is_subway=False,  # not supported yet
                        community=props.get('Gemeindename'),
                    )
                    instance.save()
                    num_created += 1
                else:
                    instance.name = props.get('Bahnhof')
                    instance.location = Point(feature["geometry"]["coordinates"])
                    instance.travellers = travellers
                    instance.post_code = props.get('PLZ')
                    instance.is_long_distance = self.is_long_distance(feature)
                    instance.is_light_rail = self.is_light_rail(feature)
                    instance.is_subway = False  # not supported yet
                    instance.community = props.get('Gemeindename')
                    instance.save()
                    num_updated += 1

            self.stdout.write(f'Created {num_created} stations')
            if num_updated > 0:
                self.stdout.write(f'Updated {num_updated} stations')
