from rest_framework import serializers
from .models import (
    Planning,
    PlanningSection,
    PlanningSectionDetails,
    Profile,
    Question
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('text', 'answer')


class PlanningSerializer(serializers.ModelSerializer):
    faq = QuestionSerializer(many=True)
    class Meta:
        model = Planning
        fields = (
            'title',
            'description',
            'short_description',
            'costs',
            'draft',
            'start_of_construction',
            'completion',
            'phase',
            'responsible',
            'url',
            'cross_section_photo',
            'faq'
        )


class PlanningSectionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningSectionDetails
        fields = (
            'side',
            'orientation',
            'length',
            'crossings',
            'speed_limit',
            'daily_traffic',
            'daily_traffic_heavy',
            'daily_traffic_cargo',
            'daily_traffic_bus',
            'rva1',
            'rva2',
            'rva3',
            'rva4',
            'rva5',
            'rva6',
            'rva7',
            'rva8',
            'rva9',
            'rva10',
            'rva11',
            'rva12',
            'rva13',
        )


class PlanningSectionSerializer(serializers.ModelSerializer):
    details = PlanningSectionDetailsSerializer(many=True)
    plannings = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='planning')

    class Meta:
        model = PlanningSection
        fields = ('id', 'name', 'description', 'details', 'plannings')


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Profile
        fields = '__all__'
