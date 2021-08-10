from rest_framework import serializers

from .models import Signup, EventSignup, Station


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
