import boto3
import botocore
from django.conf import settings
from django.db import models
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from .models import EventPermit


# Listing of events that only includes essential information
class EventListingSerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    """Returns the spelled-out name of the park area"""

    def get_location(self, obj):
        try:
            if obj.area_category == 'parking':
                return obj.address
            else:
                return EventPermit.AREA_PARK_NAMES[obj.area_park_name][1]
        except:
            return 'Keine Ortsangabe'

    class Meta:
        model = EventPermit
        fields = [
            'id',
            'title',
            'description',
            'event_start',
            'event_end',
            'date',
            'area',
            'area_category',
            'location',
        ]


class EventPermitSerializer(serializers.ModelSerializer):
    area = GeometryField(precision=14, required=False, allow_null=True, default=None)
    is_public_benefit = serializers.SerializerMethodField()
    area_park_name_long = serializers.SerializerMethodField()

    """Returns true if a public benefit attachment is set on the permit"""

    def get_is_public_benefit(self, obj):
        return bool(obj.public_benefit)

    """Returns the spelled-out name of the park area"""

    def get_area_park_name_long(self, obj):
        return (
            EventPermit.AREA_PARK_NAMES[obj.area_park_name][1]
            if obj.area_park_name is not None
            else None
        )

    class Meta:
        model = EventPermit
        fields = [
            'email',
            'tos_accepted',
            'agreement_accepted',
            'followup_accepted',
            'category',
            'org_name',
            'first_name',
            'last_name',
            'phone',
            'address',
            'date',
            'setup_start',
            'event_start',
            'event_end',
            'teardown_end',
            'num_participants',
            'area_category',
            'area',
            'title',
            'description',
            'details',
            'event_address',
            'status',
            'application_received',
            'application_decided',
            'permit_start',
            'permit_end',
            'note',
            'area_park_name',
            'is_public_benefit',
            'area_park_name_long',
        ]

        read_only_fields = [
            'status',
            'application_received',
            'application_decided',
            'permit_start',
            'permit_end',
            'note',
            'area_park_name',
            'event_address',
            'setup_sketch',
            'insurance',
            'agreement',
            'public_benefit',
            'is_public_benefit',
            'area_park_name_long',
        ]

    def validate(self, values):
        """Validate that the given S3 key exists in current bucket"""
        s3 = boto3.resource('s3')

        fields = ['insuranceS3', 'agreementS3']
        if self.initial_data.get('public_benefitS3') is not None:
            fields.append('public_benefitS3')
        if self.initial_data.get('setup_sketchS3') is not None:
            fields.append('setup_sketchS3')

        for field in fields:
            try:
                s3.Object(
                    settings.AWS_STORAGE_BUCKET_NAME,
                    self.initial_data.get(field),
                ).load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    raise serializers.ValidationError(f"Missing upload: {field}")
                raise
            except ValueError as e1:
                if self.initial_data.get(field) is None:
                    raise serializers.ValidationError(f"Missing upload: {field}")
                raise
        return values


class EventPermitDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPermit
        fields = ['insurance', 'agreement', 'public_benefit', 'setup_sketch']
