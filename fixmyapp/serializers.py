from django.db import models
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


PLACEHOLDER_PHOTO = {
    'copyright': ' Photo by Anthony Ginsbrook',
    'src': 'photos/Platzhalter_anthony-ginsbrook-225252-unsplash.jpg'
}


class ListWithDefaultSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        iterable = data.all() if isinstance(data, models.Manager) else data

        if len(iterable) == 0 and type(self.default) == list:
            iterable = self.default

        return [
            self.child.to_representation(item) for item in iterable
        ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('text', 'answer')


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ('copyright', 'src')
        list_serializer_class = ListWithDefaultSerializer


class NestedPlanningSectionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanningSectionDetails
        fields = ('length')


class NestedPlanningSectionSerializer(serializers.ModelSerializer):
    details = NestedPlanningSectionDetailsSerializer(many=True)

    class Meta:
        model = PlanningSection
        fields = ('url', 'name', 'suffix', 'details')


class PlanningSerializer(serializers.HyperlinkedModelSerializer):
    faq = QuestionSerializer(many=True)
    photos = PhotoSerializer(many=True, default=[Photo(**PLACEHOLDER_PHOTO)])
    geometry = GeometryField(precision=14)
    center = GeometryField(precision=14)
    planning_sections = NestedPlanningSectionSerializer(
        many=True,
        read_only=True,
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
            'center',
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
    geometry = GeometryField(precision=14)
    details = PlanningSectionDetailsSerializer(many=True)
    plannings = PlanningSerializer(many=True)

    class Meta:
        model = PlanningSection
        fields = (
            'url',
            'name',
            'suffix',
            'street_category',
            'geometry',
            'details',
            'plannings'
        )


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Profile
        fields = '__all__'


class FeedbackSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    subject = serializers.CharField(default='')
    message = serializers.CharField(required=True)
