import json
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from django.test import TestCase
from django.test.client import Client
from rest_framework import serializers


class EventPermitsTest(TestCase):

    registration_data = {
        "org_name": "",
        "first_name": "Marty",
        "last_name": "Party",
        "phone": "030 123 45 67",
        "address": "Mondstraße 30, 12345 Berlin",
        "date": "2021-08-15",
        "setup_start": "10:00",
        "event_start": "12:00",
        "event_end": "18:00",
        "teardown_end": "20:00",
        "num_participants": "1",
        "area_category": "park",
        "area": {
            "coordinates": [
                [
                    [13.410535484940738, 52.49072668774559],
                    [13.410577657647309, 52.490692449689845],
                    [13.41022621842427, 52.490529818559736],
                    [13.41018638864611, 52.49056548333263],
                    [13.410535484940738, 52.49072668774559],
                ]
            ],
            "type": "Polygon",
        },
        "title": "Mondscheinparty (aber tagsüber)",
        "description": "Gesänge und anbeeten des Mondes",
        "details": "Das hier ist das Veranstaltungskonzept.\n\nHier ist ein Absatz.",
        "email": "test-076@vincentahrend.com",
        "tos_accepted": True,
        "agreement_accepted": True,
        "insuranceS3": "xhain2021/events/insurance/2021-04-15_16-03-37/test.pdf",
        "agreementS3": "xhain2021/events/agreement/2021-04-15_16-03-58/test.pdf",
        "public_benefitS3": "xhain2021/events/public_benefit/2021-04-15_16-04-09/test.pdf",
        "campaign": "xhain2021",
    }

    def setUp(self):
        self.client = Client()

    def test_application(self):
        with self.settings(TOGGLE_EVENT_SIGNUPS=True):
            response = self.client.post(
                '/api/permits/events/xhain2021',
                data=json.dumps(self.registration_data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 201, response.content)

        with self.settings(TOGGLE_EVENT_SIGNUPS=False):
            response = self.client.post(
                '/api/permits/events/xhain2021',
                data=json.dumps(self.registration_data),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 405, response.content)

    def test_campaign_open_close_time(self):
        date_past = (datetime.now(tz=timezone.utc) - timedelta(days=3)).strftime(
            "%Y-%m-%d"
        )
        date_future = (datetime.now(tz=timezone.utc) + timedelta(days=3)).strftime(
            "%Y-%m-%d"
        )

        params = [
            (date_past, date_future, 201),
            (date_past, date_past, 405),
            (date_future, date_future, 405),
        ]

        for d1, d2, status_code in params:
            with self.settings(EVENT_SIGNUPS_OPEN=d1, EVENT_SIGNUPS_CLOSE=d2):
                response = self.client.post(
                    '/api/permits/events/xhain2021',
                    data=json.dumps(self.registration_data),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, status_code, response.content)


class EventPermitsAdminTest(TestCase):
    pass