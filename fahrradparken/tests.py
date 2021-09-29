import json
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from pprint import pformat, pprint
import uuid

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
    fixtures = ['station', 'survey_station']

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
