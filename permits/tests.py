import json
from datetime import datetime, timedelta, timezone
from unittest.mock import call, patch
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from rest_framework import serializers


class EventPermitsTest(TestCase):

    fixtures = ['events']

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
        with patch("permits.serializers.boto3") as boto3:
            response = self.client.post(
                '/api/permits/events/xhain2021',
                data=json.dumps(self.registration_data),
                content_type="application/json",
            )

            # Test that S3 objects are accessed
            s3 = boto3.resource.return_value
            s3.Object.assert_has_calls(
                [
                    call(
                        settings.AWS_STORAGE_BUCKET_NAME,
                        self.registration_data.get(field_name_s3),
                    )
                    for field_name_s3 in [
                        'insuranceS3',
                        'agreementS3',
                        'public_benefitS3',
                    ]
                ],
                any_order=True,
            )

        self.assertEqual(response.status_code, 201, response.content)

        invalid_registration_data = self.registration_data.copy()
        invalid_registration_data.update(first_name=None)

        response = self.client.post(
            '/api/permits/events/xhain2021',
            data=json.dumps(invalid_registration_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400, response.content)

    def test_campaign_open_close_time(self):
        date_past = (datetime.now(tz=timezone.utc) - timedelta(minutes=3)).isoformat()
        date_future = (datetime.now(tz=timezone.utc) + timedelta(minutes=3)).isoformat()

        params = [
            # Application should be possible if times are underdefined
            (None, None, 201),
            (date_past, None, 201),
            (None, date_future, 201),
            # Times should be respoected when set
            (date_past, date_future, 201),
            (date_past, date_past, 405),
            (date_future, date_future, 405),
            # Application should be closed when there is a configuration error
            ('<invalid datetime>', date_future, 405),
        ]

        for date_1, date_2, status_code in params:
            with self.settings(
                EVENT_SIGNUPS_OPEN=date_1,
                EVENT_SIGNUPS_CLOSE=date_2,
            ):
                with patch("permits.serializers.boto3") as boto3:
                    response = self.client.post(
                        '/api/permits/events/xhain2021',
                        data=json.dumps(self.registration_data),
                        content_type="application/json",
                    )
                self.assertEqual(
                    response.status_code,
                    status_code,
                    f"Unexpected status {response.status_code} opening between {date_1} and {date_2}",
                )

    def test_listing(self):
        """Test endpoint for listing future accepted applications."""
        response = self.client.get(
            '/api/permits/events/xhain2021/listing', content_type="application/json"
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(response.json()), 2)


class EventPermitsAdminTest(TestCase):
    pass
