from rest_framework import serializers
from .models import Survey


class SurveySerializer(serializers.ModelSerializer):

    class Meta:
        model = Survey
        fields = ('id', 'profile', 'project')
