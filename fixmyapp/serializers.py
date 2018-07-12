from rest_framework import serializers
from .models import PlanningSection, PlanningSectionDetails, Profile


class PlanningSectionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningSectionDetails
        fields = (
            'side',
            'orientation',
            'length',
            'crossings',
        )


class PlanningSectionSerializer(serializers.ModelSerializer):
    details = PlanningSectionDetailsSerializer(many=True)

    class Meta:
        model = PlanningSection
        fields = ('id', 'name', 'description', 'details')


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Profile
        fields = '__all__'
