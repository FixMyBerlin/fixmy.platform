import datetime
import json
import tempfile
import uuid
from django.core import mail
from django.test import TestCase, override_settings
from django.test.client import Client

from .models import Station, SurveyStation


signup_request = {
    "affiliation": 'Gemeinde Seeblick',
    "first_name": "Juliane M",
    "last_name": "Kalb",
    "role": 'Verkehrsplanerin',
    "email": "juliane.m.kalb@example.net",
    "phone": "09621 49 94 98",
    "station_name": 'Bahnhof Wassersuppe',
    "message": '',
}

event_request = dict(signup_request)
event_request['event_id'] = 1
event_request['event_title'] = 'Webinar Flaechenberechnung in Excel'
event_request['event_date'] = '29.August 2021'
event_request['event_time'] = '16:00 Uhr'
event_request['newsletter'] = False


survey_station_request = {
    'session': '4e86d361-87a3-4e14-bd3a-fcf9003f7dd8',
    'station': 1,
    'survey_version': 1,
    'npr': 9,
    'annoyances': '1,5',
    'annoyance_custom': '',
    'requested_location': 'Westseite',
}

survey_bicycle_usage_request = {
    'session': '4e86d361-87a3-4e14-bd3a-fcf9003f7dd8',
    'survey_version': 1,
    'frequency': 2,
    'reasons': '2,3',
    'reason_custom': '',
    'duration': 1,
    'with_children': False,
    'purpose': 3,
    'rating_racks': 3,
    'rating_sheltered_racks': 3,
    'rating_bike_box': 3,
    'rating_bike_quality': 3,
    'rating_road_network': 3,
    'rating_train_network': 3,
    'rating_services': 3,
    'price': 1,
    'age': 2,
}


class SignupTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        from .models import Signup

        response = self.client.post(
            '/api/fahrradparken/signup',
            data=json.dumps(signup_request),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Signup.objects.count(), 1)

        self.assertEqual(len(mail.outbox), 1, mail.outbox)
        email_body = mail.outbox[0].message()._payload
        self.assertTrue(signup_request['first_name'] in email_body, email_body)
        self.assertTrue(event_request['event_title'] not in email_body, email_body)

    def test_invalid_signup(self):
        from .models import Signup

        invalid_signup = dict(signup_request)
        invalid_signup.update(affiliation='')

        response = self.client.post(
            '/api/fahrradparken/signup',
            data=json.dumps(invalid_signup),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400, response.content)
        self.assertEqual(Signup.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0, mail.outbox)
        self.assertEqual(
            response.content,
            b'{"affiliation":["Dieses Feld darf nicht leer sein."]}',
            response.content,
        )

    def test_event_signup(self):
        from .models import EventSignup

        response = self.client.post(
            '/api/fahrradparken/signup',
            data=json.dumps(event_request),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(EventSignup.objects.count(), 1)

        self.assertEqual(len(mail.outbox), 1, mail.outbox)
        email_body = mail.outbox[0].message()._payload
        self.assertTrue(signup_request['first_name'] in email_body, email_body)
        self.assertTrue(event_request['event_title'] in email_body, email_body)


class StationTest(TestCase):
    fixtures = ['station', 'survey_station', 'parking_facilities']

    def setUp(self):
        self.client = Client()

    def test_get_listing(self):
        response = self.client.get(
            '/api/fahrradparken/stations', content_type='application/json'
        )
        self.assertEqual(response.status_code, 200, response.content)

        data = response.json()
        self.assertEqual(len(data['features']), 3)

        # Listing should not contain user data
        self.assertFalse('annoyances' in data['features'][0]['properties'])

    def test_get_full_listing(self):
        """Include dynamic data in listing."""
        response = self.client.get(
            '/api/fahrradparken/stations?full', content_type='application/json'
        )
        self.assertEqual(response.status_code, 200, response.content)

        data = response.json()
        self.assertEqual(len(data['features']), 3)

        # Listing should contain user data
        self.assertTrue('annoyances' in data['features'][0]['properties'])

    def test_search_query(self):
        response = self.client.get(
            '/api/fahrradparken/stations',
            {'search': 'rothe'},
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200, response.content)

        data = response.json()
        self.assertEqual(len(data['features']), 1)
        self.assertEqual(data['features'][0]['geometry']['type'], 'Point')

    def test_get_detail(self):
        station = Station.objects.all()[0]
        url = f'/api/fahrradparken/stations/{station.id}'
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 200, response.content)
        props = response.json()['properties']
        self.assertEqual(props['annoyances'], {'1': 1, '5': 1})
        self.assertEqual(
            props['annoyances_custom'], ['Die Leute drehen immer meinen Sattel um.']
        )
        self.assertEqual(
            props['net_promoter_score'],
            {
                'rating': 1.0,
                'total_count': 1,
                'promoter_count': 1,
                'detractor_count': 0,
            },
        )
        self.assertEqual(props['requested_locations'], ['Westseite'])
        self.assertEqual(props['photos'], [])

    def test_missing_get_detail(self):
        """Test error response."""
        url = f'/api/fahrradparken/stations/9999'
        response = self.client.get(url, content_type='application/json')
        self.assertEqual(response.status_code, 404, response.content)

    def test_annoyances(self):
        response = self.client.get('/api/fahrradparken/stations/2')
        self.assertIn('annoyances', response.json().get('properties', {}))


class SurveyStationTest(TestCase):
    fixtures = ['station']

    def setUp(self):
        self.client = Client()

    def test_post_station_survey(self):
        """Posting a station survey with valid data should succeed."""
        response = self.client.post(
            '/api/fahrradparken/survey/station',
            data=json.dumps(survey_station_request),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201, response.content)

        data = response.json()
        self.assertTrue(len(data.keys()) > 0)

    def test_post_station_survey_invalid(self):
        """Requests missing data fields should fail."""
        invalid_survey_station_request = survey_station_request.copy()
        del invalid_survey_station_request['station']

        response = self.client.post(
            '/api/fahrradparken/survey/station',
            data=json.dumps(invalid_survey_station_request),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_post_bicycle_usage_survey(self):
        """Posting bicycle usage following a station survey should succeed."""

        self.client.post(
            '/api/fahrradparken/survey/station',
            data=json.dumps(survey_station_request),
            content_type='application/json',
        )
        response = self.client.post(
            '/api/fahrradparken/survey/bicycle-usage',
            data=json.dumps(survey_bicycle_usage_request),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201, response.content)

    def test_post_bicycle_usage_survey_failing(self):
        """Posting bicycle usage without leading with a station survey should fail."""
        response = self.client.post(
            '/api/fahrradparken/survey/bicycle-usage',
            data=json.dumps(survey_bicycle_usage_request),
            content_type='application/json',
        )
        # fails because the survey refers to non-existing station survey id
        self.assertEqual(response.status_code, 400, response.content)


class SurveyInfoViewTest(TestCase):
    fixtures = ['station', 'survey_station', 'parking_facilities']

    def test_get_info(self):
        response = self.client.get('/api/fahrradparken/info')
        self.assertEqual(response.json().get('survey_stations_count', 0), 4)
        self.assertEqual(response.json().get('survey_stations_session_count', 0), 3)
        self.assertEqual(response.json().get('survey_stations_with_nps_count', 0), 1)
        self.assertEqual(response.json().get('survey_bicycle_usage_count"', 0), 0)
        self.assertEqual(
            response.json().get('survey_stations_with_parking_facilities_count', 0), 3
        )
        self.assertEqual(response.json().get('survey_parking_facilities_count', 0), 8)
        self.assertEqual(
            response.json().get('survey_confirmed_parking_facilities_count', 0), 4
        )


class UniqueUUIDTest(TestCase):
    fixtures = ['station', 'survey_station']

    def test_stations_by_uuid(self):
        """Request list of stations for which a UUID has answered the survey."""
        session = SurveyStation.objects.first().session
        response = self.client.get(f'/api/fahrradparken/uuid/{str(session)}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertListEqual(data, [{'station_id': 1}, {'station_id': 2}])

    def test_stations_by_uuid(self):
        """If no answers have been submitted an empty list is returned."""
        response = self.client.get(f'/api/fahrradparken/uuid/{str(uuid.uuid4())}')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertListEqual(data, [])


class CheckPreviousBicycleSurveyTest(TestCase):
    fixtures = ['station', 'survey_station']

    def test_check_previous_bicycle_survey(self):
        session = SurveyStation.objects.first().session
        response = self.client.get(
            f'/api/fahrradparken/uuid/{str(session)}/bicycle-usage-survey'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        # Improve this test by adding a fixture that allows testing for
        # {'doesExist': True}
        self.assertEqual(data, {'doesExist': False})


class RawDataExportTest(TestCase):
    fixtures = ['station', 'survey_station']

    def test_station_survey_raw_export(self):
        response = self.client.get('/api/fahrradparken/survey-results/stations')
        self.assertContains(
            response, SurveyStation.objects.first().session, 2, status_code=200
        )


@override_settings(
    DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage',
    MEDIA_ROOT=tempfile.mkdtemp(),
)
class ParkingFacilityTest(TestCase):
    fixtures = ['station']

    def test_create_and_update_parking_facility(self):
        initial_report = {
            'capacity': 10,
            'condition': 0,
            'confirm': False,
            'covered': True,
            'description': 'Lorem ipsum dolor sit amet',
            'location': {'type': 'Point', 'coordinates': [13.415941, 52.494432]},
            'occupancy': 0,
            'parking_garage': False,
            'photo': {
                'photo_url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0lEQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6P9/AFGGFyjOXZtQAAAAAElFTkSuQmCC',
                'description': 'Lorem ipsum',
            },
            'secured': False,
            'stands': True,
            'station': 2,
            'two_tier': False,
            'type': 0,
        }
        response = self.client.post(
            f'/api/fahrradparken/parking-facilities',
            data=json.dumps(initial_report),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json())
        self.assertIn('url', response.json())
        self.assertEqual(response.json().get('condition'), 0)
        self.assertFalse(response.json().get('confirmations'), 0)
        self.assertEqual(
            response.json().get('description'), 'Lorem ipsum dolor sit amet'
        )
        self.assertEqual(response.json().get('occupancy'), 0)
        self.assertEqual(len(response.json().get('photos', [])), 1)
        self.assertFalse(response.json()['photos'][0].get('is_published'))
        self.assertIsNone(response.json()['photos'][0].get('photo_url'))
        self.assertIsNone(response.json()['photos'][0].get('description'))
        self.assertEqual(response.json().get('external_id'), '2.1')

        updated_report = {
            'capacity': 10,
            'condition': 3,
            'confirm': True,
            'covered': True,
            'location': {'type': 'Point', 'coordinates': [13.415941, 52.494432]},
            'occupancy': 2,
            'parking_garage': False,
            'photo': {
                'photo_url': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQAQMAAAAlPW0iAAAABlBMVEUAAAD///+l2Z/dAAAAM0lEQVR4nGP4/5/h/1+G/58ZDrAz3D/McH8yw83NDDeNGe4Ug9C9zwz3gVLMDA/A6P9/AFGGFyjOXZtQAAAAAElFTkSuQmCC',
                'description': 'Lorem ipsum',
            },
            'secured': False,
            'stands': True,
            'station': 2,
            'two_tier': False,
            'type': 0,
        }
        response = self.client.put(
            f'/api/fahrradparken/parking-facilities/{response.json().get("id")}',
            data=json.dumps(updated_report),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('condition'), 2)
        self.assertEqual(response.json().get('confirmations'), 1)
        self.assertEqual(response.json().get('occupancy'), 1)
        self.assertEqual(len(response.json().get('photos', [])), 2)

        confirmed_report = {
            'capacity': 10,
            'condition': 0,
            'confirm': True,
            'covered': True,
            'location': {'type': 'Point', 'coordinates': [13.415941, 52.494432]},
            'occupancy': 0,
            'parking_garage': False,
            'secured': False,
            'stands': True,
            'station': 2,
            'two_tier': False,
            'type': 0,
        }
        response = self.client.put(
            f'/api/fahrradparken/parking-facilities/{response.json().get("id")}',
            data=json.dumps(confirmed_report),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json().get('condition'), 1)
        self.assertEqual(response.json().get('confirmations'), 2)
        self.assertEqual(response.json().get('occupancy'), 1)

        response = self.client.get('/api/fahrradparken/stations/2')
        self.assertIn('parking_facilities', response.json()['properties'])
        self.assertEqual(len(response.json()['properties']['parking_facilities']), 1)

    def test_occupancy_and_condition_can_be_added(self):
        initial_report = {
            'capacity': 10,
            'confirm': False,
            'covered': True,
            'location': {'type': 'Point', 'coordinates': [13.415941, 52.494432]},
            'parking_garage': False,
            'secured': False,
            'stands': True,
            'station': 2,
            'two_tier': False,
            'type': 0,
        }
        response = self.client.post(
            f'/api/fahrradparken/parking-facilities',
            data=json.dumps(initial_report),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)

        response = self.client.patch(
            f'/api/fahrradparken/parking-facilities/{response.json().get("id")}',
            data=json.dumps({'occupancy': '1'}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.patch(
            f'/api/fahrradparken/parking-facilities/{response.json().get("id")}',
            data=json.dumps({'condition': '1'}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_type_is_optional_and_can_be_set_to_null(self):
        updated_report = initial_report = {
            'capacity': 10,
            'confirm': False,
            'covered': True,
            'location': {'type': 'Point', 'coordinates': [13.415941, 52.494432]},
            'parking_garage': False,
            'secured': False,
            'stands': True,
            'station': 2,
            'two_tier': False,
            'type': 0,
        }

        response = self.client.post(
            f'/api/fahrradparken/parking-facilities',
            data=json.dumps(initial_report),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 201)

        updated_report['type'] = None
        response = self.client.put(
            f'/api/fahrradparken/parking-facilities/{response.json().get("id")}',
            data=json.dumps(updated_report),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.json().get('type'))

    def test_list_parking_facilities(self):
        response = self.client.get('/api/fahrradparken/parking-facilities')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
