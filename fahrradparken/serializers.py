import boto3
import botocore
import json
from django.conf import settings
from drf_extra_fields.fields import HybridImageField
from rest_framework import serializers

from .models import (
    EventSignup,
    ParkingFacility,
    ParkingFacilityCondition,
    ParkingFacilityOccupancy,
    ParkingFacilityPhoto,
    Signup,
    Station,
    SurveyBicycleUsage,
    SurveyStation,
)


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signup
        exclude = ['modified_date']


class EventSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSignup
        exclude = ['modified_date']


class ParkingFacilityPhotoSerializer(serializers.ModelSerializer):
    is_published = serializers.BooleanField(read_only=True)
    photo_url = HybridImageField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if not instance.is_published:
            ret = {k: ret[k] if k == 'is_published' else None for k in ret.keys()}
        return ret

    class Meta:
        model = ParkingFacilityPhoto
        fields = ('description', 'is_published', 'photo_url', 'terms_accepted')


class ParkingFacilitySerializer(serializers.ModelSerializer):
    condition = serializers.IntegerField(required=False)
    confirm = serializers.BooleanField(write_only=True)
    occupancy = serializers.IntegerField(required=False)
    photo = ParkingFacilityPhotoSerializer(required=False, write_only=True)
    photos = ParkingFacilityPhotoSerializer(many=True, read_only=True)
    station = serializers.PrimaryKeyRelatedField(
        many=False, queryset=Station.objects.all()
    )

    class Meta:
        model = ParkingFacility
        fields = [
            'capacity',
            'condition',
            'confirm',
            'confirmations',
            'covered',
            'created_date',
            'external_id',
            'id',
            'location',
            'occupancy',
            'parking_garage',
            'photo',
            'photos',
            'secured',
            'source',
            'stands',
            'station',
            'two_tier',
            'type',
            'url',
        ]
        extra_kwargs = {
            'url': {'view_name': 'fahrradparken:parkingfacility-detail'},
        }

    def create(self, validated_data):
        condition = validated_data.pop('condition', None)
        occupancy = validated_data.pop('occupancy', None)
        photo = validated_data.pop('photo', None)
        validated_data.pop('confirm')
        validated_data['external_id'] = ParkingFacility.next_external_id(
            validated_data['station']
        )
        parking_facility = ParkingFacility.objects.create(**validated_data)
        if condition is not None:
            ParkingFacilityCondition.objects.create(
                parking_facility=parking_facility, value=condition
            )
        if occupancy is not None:
            ParkingFacilityOccupancy.objects.create(
                parking_facility=parking_facility, value=occupancy
            )
        if photo:
            ParkingFacilityPhoto.objects.create(
                parking_facility=parking_facility, **photo
            )
        return parking_facility

    def update(self, instance, validated_data):
        condition = validated_data.pop('condition', None)
        occupancy = validated_data.pop('occupancy', None)
        photo = validated_data.pop('photo', None)
        if condition is not None:
            ParkingFacilityCondition.objects.create(
                parking_facility=instance, value=condition
            )
        if occupancy is not None:
            ParkingFacilityOccupancy.objects.create(
                parking_facility=instance, value=occupancy
            )
        if photo:
            ParkingFacilityPhoto.objects.create(parking_facility=instance, **photo)

        confirm = validated_data.pop('confirm', None)

        if confirm is not None:
            if confirm:
                instance.confirmations += 1
            else:
                instance.confirmations = 0

        return super().update(instance, validated_data)


class StationSerializer(serializers.ModelSerializer):
    annoyances_custom = serializers.ReadOnlyField()
    annoyances = serializers.ReadOnlyField()
    net_promoter_score = serializers.ReadOnlyField()
    parking_facilities = ParkingFacilitySerializer(many=True, read_only=True)
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
