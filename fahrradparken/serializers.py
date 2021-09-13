import boto3
import botocore
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
    class Meta:
        model = Station
        exclude = ['modified_date']


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
