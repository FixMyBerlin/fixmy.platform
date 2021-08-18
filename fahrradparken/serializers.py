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


    class Meta:
        model = SurveyStation
        exclude = ['modified_date']


class SurveyBicycleUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyBicycleUsage
        exclude = ['modified_date']
