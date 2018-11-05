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
    'copyright': 'Photo by Anthony Ginsbrook',
    'src': 'photos/Platzhalter_anthony-ginsbrook-225252-unsplash.jpg'
}


ANOTHER_PLACEHOLDER_PHOTO = {
    'copyright': 'Photo by Emil Bruckner',
    'src': 'photos/emil-bruckner-532523-unsplash.jpg'
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
    advisory_bike_lane_ratio = serializers.DecimalField(None, 3)
    bike_lane_ratio = serializers.DecimalField(None, 3)
    bike_path_ratio = serializers.DecimalField(None, 3)
    cycling_infrastructure_ratio = serializers.DecimalField(None, 3)
    cycling_infrastructure_safety = serializers.DecimalField(None, 1)
    happy_bike_index = serializers.DecimalField(None, 1)
    length = serializers.DecimalField(None, 2)
    protected_bike_lane_ratio = serializers.DecimalField(None, 3)
    road_type = serializers.DecimalField(None, 1)
    safety_index = serializers.DecimalField(None, 1)
    shared_use_path_ratio = serializers.DecimalField(None, 3)
    velocity_index = serializers.DecimalField(None, 1)

    class Meta:
        model = PlanningSectionDetails
        fields = (
            'advisory_bike_lane_ratio',
            'bike_lane_ratio',
            'bike_path_ratio',
            'cycling_infrastructure_ratio',
            'cycling_infrastructure_safety',
            'happy_bike_index',
            'length',
            'orientation',
            'protected_bike_lane_ratio',
            'road_type',
            'safety_index',
            'shared_use_path_ratio',
            'side',
            'velocity_index',
        )


class NestedPlanningSectionSerializer(serializers.ModelSerializer):
    details = NestedPlanningSectionDetailsSerializer(many=True)

    class Meta:
        model = PlanningSection
        fields = ('url', 'name', 'suffix', 'borough', 'details')


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
    likes = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return obj.likes.count()

    def get_liked_by_user(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).count() > 0
        else:
            return False

    class Meta:
        model = Planning
        fields = (
            'url',
            'title',
            'description',
            'short_description',
            'category',
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
            'likes',
            'liked_by_user',
        )


class PlanningSectionDetailsSerializer(serializers.ModelSerializer):
    advisory_bike_lane_ratio = serializers.DecimalField(None, 3)
    bike_lane_ratio = serializers.DecimalField(None, 3)
    bike_path_ratio = serializers.DecimalField(None, 3)
    cycling_infrastructure_ratio = serializers.DecimalField(None, 3)
    cycling_infrastructure_safety = serializers.DecimalField(None, 1)
    happy_bike_index = serializers.DecimalField(None, 1)
    length = serializers.DecimalField(None, 2)
    photos = PhotoSerializer(many=True, default=[Photo(**ANOTHER_PLACEHOLDER_PHOTO)])
    protected_bike_lane_ratio = serializers.DecimalField(None, 3)
    road_type = serializers.DecimalField(None, 1)
    safety_index = serializers.DecimalField(None, 1)
    shared_use_path_ratio = serializers.DecimalField(None, 3)
    velocity_index = serializers.DecimalField(None, 1)

    class Meta:
        model = PlanningSectionDetails
        fields = (
            'advisory_bike_lane_ratio',
            'bike_lane_ratio',
            'bike_path_ratio',
            'crossings',
            'cycling_infrastructure_ratio',
            'cycling_infrastructure_safety',
            'daily_traffic',
            'daily_traffic_heavy',
            'daily_traffic_cargo',
            'daily_traffic_bus',
            'happy_bike_index',
            'length',
            'orientation',
            'photos',
            'protected_bike_lane_ratio',
            'road_type',
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
            'safety_index',
            'shared_use_path_ratio',
            'side',
            'speed_limit',
            'velocity_index',
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
            'borough',
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
