from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from .models import (
    Photo,
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


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('copyright', 'src')


class PlanningSerializer(serializers.HyperlinkedModelSerializer):
    faq = QuestionSerializer(many=True)
    photos = PhotoSerializer(many=True)
    geometry = GeometryField(precision=14)
    planning_sections = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='planningsection-detail'
    )
    planning_section_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True,
        source='planning_sections'
    )

    class Meta:
        model = Planning
        fields = (
            'url',
            'title',
            'description',
            'short_description',
            'side',
            'costs',
            'draft_submitted',
            'construction_started',
            'construction_completed',
            'phase',
            'responsible',
            'external_url',
            'cross_section_photo',
            'faq',
            'planning_sections',
            'planning_section_ids',
            'geometry',
            'photos',
        )


class PlanningSectionDetailsSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True)

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
            'photos'
        )


class PlanningSectionSerializer(serializers.HyperlinkedModelSerializer):
    details = PlanningSectionDetailsSerializer(many=True)
    plannings = PlanningSerializer(many=True)

    class Meta:
        model = PlanningSection
        fields = (
            'url',
            'name',
            'description',
            'street_category',
            'details',
            'plannings'
        )


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Profile
        fields = '__all__'
