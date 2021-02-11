import json
import tempfile
from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch
from decimal import Decimal
from collections import OrderedDict

from fixmyapp.models import Section, SectionAccidents
from fixmyapp.serializers import SectionAccidentsSerializer, SectionDetailsSerializer


class ImportSectionAccidents(TestCase):
    fixtures = ['sections']

    def setUp(self):
        self.section = Section.objects.all().first()

    def test_import_valid_data(self):
        """Test importing a valid accident dataset."""

        raw_section_accidents = f"""section_id,killed,severely_injured,slightly_injured,source,risk_level,side
{self.section.id},0,1,0,"Bundesministerium für Verkehr und digitale Infrastruktur (2017 - 2018).
Unfallatlas, Statistische Ämter des Bundes und der Länder (2019).",1,2
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.csv'
        ) as f:
            f.write(raw_section_accidents)
            f.seek(0)
            call_command('importsectionaccidents', f.name, skip_confirmation=True)

        self.assertEqual(self.section.accidents.count(), 1)

        section_accidents_serialized = SectionAccidentsSerializer(
            self.section.accidents.first()
        ).data
        section_accidents_expected = {
            'killed': 0,
            'severely_injured': 1,
            'slightly_injured': 0,
            'side': 2,
            'source': 'Bundesministerium für Verkehr und digitale Infrastruktur (2017 - 2018).\nUnfallatlas, Statistische Ämter des Bundes und der Länder (2019).',
            'risk_level': 1,
        }
        self.assertDictEqual(section_accidents_serialized, section_accidents_expected)

    def test_missing_column(self):
        """Test importing dataset with a missing column."""

        raw_section_accidents = f"""section_id,killed,severely_injured,slightly_injured,source,risk_level
{self.section.id},0,1,0,"Bundesministerium für Verkehr und digitale Infrastruktur (2017 - 2018).
Unfallatlas, Statistische Ämter des Bundes und der Länder (2019).",1
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.csv'
        ) as f:
            f.write(raw_section_accidents)
            f.seek(0)
            with self.assertRaises(SystemExit):
                call_command('importsectionaccidents', f.name, skip_confirmation=True)

    def test_encoding_error(self):
        """Test importing dataset with a wrong file encoding."""

        raw_section_accidents = f"""section_id,killed,severely_injured,slightly_injured,source,risk_level,side
{self.section.id},0,1,0,"Bundesministerium für Verkehr und digitale Infrastruktur (2017 - 2018).
Unfallatlas, Statistische Ämter des Bundes und der Länder (2019).",1,2
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="ISO-8859-1", suffix='.csv'
        ) as f:
            f.write(raw_section_accidents)
            f.seek(0)
            with self.assertRaises(SystemExit):
                call_command('importsectionaccidents', f.name, skip_confirmation=True)


class ImportSectionDetails(TestCase):
    fixtures = ['sections']

    def setUp(self):
        self.section = Section.objects.all().first()

    def test_import_valid_data(self):
        """Test importing a valid section details dataset."""

        # This test case is incomplete without also linking photos from S3
        # storage. However, testing that they are imported correctly requires
        # either letting the test case hit S3, which I would rather avoid, or
        # mocking boto3, which I don't have time for right now. If you do, please
        # add this value to the `rva_pics` column in the following sample csv
        # and update `section_details_excepted` accordingly below.
        #
        #     /fb_daten/fotos/radverkehrsanlagen/Dokumente/00000C00/0x000E2C/doci75639A09.jpg /fb_daten/fotos/radverkehrsanlagen/Dokumente/00000C00/0x000E2C/doci4AB36C34.jpg

        raw_section_details = f"""section_id,side,exist,tempolimit,dailytraffic,dailytraffic_heavy,daily_traffic_transporter,dailiy_traffic_bus,length,crossings,orientation,RVA1,RVA2,RVA3,RVA4,RVA5,RVA6,RVA7,RVA8,RVA9,RVA10,RVA11,RVA12,RVA13,hilfs,rva_pics
{self.section.id},0,1,30,5110.15,40.98,521.55,4.85,874.77,1,S,0,0.00,0,0,0,0,0,0,0,0,21.94964056,0,0,1_0,
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.csv'
        ) as f:
            f.write(raw_section_details)
            f.seek(0)
            call_command('importsectiondetails', f.name)

        self.assertEqual(self.section.details.count(), 1)

        section_details_serialized = SectionDetailsSerializer(
            self.section.details.first()
        ).data

        section_details_expected = {
            'advisory_bike_lane_ratio': Decimal('0.000'),
            'bike_lane_ratio': Decimal('0.000'),
            'bike_path_ratio': Decimal('0.000'),
            'crossings': 1,
            'cycling_infrastructure_ratio': Decimal('0.025'),
            'cycling_infrastructure_safety': Decimal('0.0'),
            'daily_traffic': Decimal('5110.15'),
            'daily_traffic_heavy': Decimal('40.98'),
            'daily_traffic_cargo': Decimal('521.55'),
            'daily_traffic_bus': Decimal('4.85'),
            'happy_bike_index': Decimal('6.3'),
            'length': Decimal('874.77'),
            'orientation': 'S',
            'photos': [
                OrderedDict(
                    [
                        ('copyright', 'Photo by Emil Bruckner'),
                        (
                            'src',
                            'https://fmb-aws-bucket.s3.amazonaws.com/photos/emil-bruckner-532523-unsplash.jpg',
                        ),
                    ]
                )
            ],
            'protected_bike_lane_ratio': Decimal('0.000'),
            'road_type': Decimal('0.6'),
            'rva1': Decimal('0E-12'),
            'rva2': Decimal('0E-12'),
            'rva3': Decimal('0E-12'),
            'rva4': Decimal('0E-12'),
            'rva5': Decimal('0E-12'),
            'rva6': Decimal('0E-12'),
            'rva7': Decimal('0E-12'),
            'rva8': Decimal('0E-12'),
            'rva9': Decimal('0E-12'),
            'rva10': Decimal('0E-12'),
            'rva11': Decimal('21.949640560000'),
            'rva12': Decimal('0E-12'),
            'rva13': Decimal('0E-12'),
            'safety_index': Decimal('5.3'),
            'shared_use_path_ratio': Decimal('0.000'),
            'side': 0,
            'speed_limit': 30,
            'velocity_index': Decimal('1.0'),
        }
        self.assertDictEqual(section_details_serialized, section_details_expected)

    def test_missing_column(self):
        """Test importing dataset with a missing column."""

        raw_section_details = f"""section_id,side,exist,tempolimit,dailytraffic,dailytraffic_heavy,daily_traffic_transporter,dailiy_traffic_bus,length,crossings,orientation,RVA1,RVA2,RVA3,RVA4,RVA5,RVA6,RVA7,RVA8,RVA9,RVA10,RVA11,RVA12,RVA13,hilfs
{self.section.id},0,1,30,5110.15,40.98,521.55,4.85,874.77,1,S,0,0.00,0,0,0,0,0,0,0,0,21.94964056,0,0,1_0
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.csv'
        ) as f:
            f.write(raw_section_details)
            f.seek(0)
            with self.assertRaises(SystemExit):
                call_command('importsectiondetails', f.name)


class ExportSectionTest(TestCase):
    fixtures = ['sections', 'sectionaccidents', 'sectiondetails']

    def test_command(self):
        """Test running the export command."""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.geojson'
        ) as f:
            call_command('exportsections', f.name)
            export = json.load(f)
            self.assertEqual(export.get('type'), 'FeatureCollection')
            self.assertEqual(type(export.get('features')), list)
            self.assertEqual(len(export.get('features')), 10)
