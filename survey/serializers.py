from rest_framework import serializers
from .models import Rating, Survey


class RatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ('duration', 'rating')


class SurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = ('id', 'profile', 'project')
