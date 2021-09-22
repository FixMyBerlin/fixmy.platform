import boto3
import botocore
import json
from django.conf import settings
from rest_framework import serializers

from .models import Signup, EventSignup, Station, SurveyBicycleUsage, SurveyStation


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        exclude = ['modified_date']


class EventSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSignup
        exclude = ['modified_date']


class StationSerializer(serializers.ModelSerializer):
    annoyances_custom = serializers.ReadOnlyField()
    annoyances = serializers.ReadOnlyField()
    net_promoter_score = serializers.ReadOnlyField()
    photos = serializers.ReadOnlyField()
    requested_locations = serializers.ReadOnlyField()

    class Meta:
        model = Station
        exclude = ('created_date', 'modified_date', 'location')

    def to_representation(self, instance):
        props = super().to_representation(instance)
        return {
            'type': 'Feature',
            'geometry': json.loads(instance.location.json),
            'properties': props,
        }


class StaticStationSerializer(serializers.ModelSerializer):
    """This serializer doesn't output dynamic user data."""

    class Meta:
        model = Station
        fields = (
            'id',
            'name',
            'community',
            'travellers',
            'post_code',
            'is_long_distance',
            'is_light_rail',
        )

    def to_representation(self, instance):
        props = super().to_representation(instance)
        return {
            'type': 'Feature',
            'geometry': json.loads(instance.location.json),
            'properties': props,
        }


class SurveyStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyStation
        exclude = ['modified_date']
        read_only_fields = ['photo']

    def validate(self, values):
        s3 = boto3.resource('s3')

        # Check that supplied photo does exist in S3
        field = 'photoS3'
        if self.initial_data.get(field) is not None:
            try:
                s3.Object(
                    settings.AWS_STORAGE_BUCKET_NAME, self.initial_data.get(field)
                )
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    raise serializers.ValidationError(f"Uploaded photo not found in S3")
                raise
        return values


class SurveyStationShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyStation
        fields = ['station_id']


class SurveyBicycleUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyBicycleUsage
        exclude = ['modified_date']
