from rest_framework import serializers
from .models import Rating, Survey


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('duration', 'rating')


class SurveySerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source='id')

    class Meta:
        model = Survey
        fields = ('session_id', 'profile', 'project')
