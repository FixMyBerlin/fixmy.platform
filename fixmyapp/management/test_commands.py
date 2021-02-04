import tempfile
from django.core.management import call_command
from django.test import TestCase
from unittest.mock import patch

from fixmyapp.models import Section, SectionAccidents

class ImportSectionAccidents(TestCase):
    fixtures = ['sections']

    def test_import_valid_data(self):
        """Test importing a valid accident dataset."""

        section = Section.objects.all().first()
        raw_section_accidents = f"""section_id,killed,severely_injured,slightly_injured,source,risk_level,side
{section.id},0,1,0,"Bundesministerium für Verkehr und digitale Infrastruktur (2017 - 2018).
Unfallatlas, Statistische Ämter des Bundes und der Länder (2019).",1,2
"""

        with tempfile.NamedTemporaryFile(
            mode="w+", encoding="UTF-8", suffix='.csv'
        ) as f:
            f.write(raw_section_accidents)
            f.seek(0)
            call_command('importsectionaccidents', f.name, skip_confirmation=True)

        self.assertEqual(section.accidents.count(), 1)