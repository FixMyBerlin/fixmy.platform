import json
from django.core import mail
from django.test import TestCase
from django.test.client import Client


signup_data = {
    "affiliation": 'Gemeinde Seeblick',
    "first_name": "Juliane M",
    "last_name": "Kalb",
    "role": 'Verkehrsplanerin',
    "email": "juliane.m.kalb@example.net",
    "phone": "09621 49 94 98",
    "station_name": 'Bahnhof Wassersuppe',
    "message": '',
}

event_data = dict(signup_data)
event_data['event_id'] = 1
event_data['event_title'] = 'Webinar Flächenberechnung in Excel'
event_data['event_date'] = '29.August 2021'
event_data['event_time'] = '16:00 Uhr'
event_data['newsletter'] = False


class SignupTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        from .models import EventSignup, Signup

        response = self.client.post(
            '/api/fahrradparken/signup',
            data=json.dumps(signup_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Signup.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1, mail.outbox)

    def test_invalid_signup(self):
        from .models import EventSignup, Signup

        invalid_signup = dict(signup_data)
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
        from .models import EventSignup, Signup

        response = self.client.post(
            '/api/fahrradparken/signup',
            data=json.dumps(event_data),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(EventSignup.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1, mail.outbox)
