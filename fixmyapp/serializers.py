from django.contrib.auth import get_user_model
from django.db import models
from drf_extra_fields.fields import HybridImageField
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from .models import (
    BikeStands,
    GastroSignup,
    PlaystreetSignup,
    Photo,
    Profile,
    Project,
    Question,
    Report,
    Section,
    SectionDetails,
)


PLACEHOLDER_PHOTO = {
    'copyright': 'Photo by Anthony Ginsbrook',
    'src': 'photos/Platzhalter_anthony-ginsbrook-225252-unsplash.jpg',
}


ANOTHER_PLACEHOLDER_PHOTO = {
    'copyright': 'Photo by Emil Bruckner',
    'src': 'photos/emil-bruckner-532523-unsplash.jpg',
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

        return [self.child.to_representation(item) for item in iterable]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ('text', 'answer')


class PhotoSerializer(serializers.ModelSerializer):
    src = HybridImageField()

    class Meta:
        model = Photo
        fields = ('copyright', 'src')
        list_serializer_class = ListWithDefaultSerializer


class NestedSectionDetailsSerializer(serializers.ModelSerializer):
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
        model = SectionDetails
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


class NestedSectionSerializer(serializers.ModelSerializer):
    details = NestedSectionDetailsSerializer(many=True)

    class Meta:
        model = Section
        fields = ('url', 'street_name', 'suffix', 'borough', 'details')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    faq = QuestionSerializer(many=True)
    photos = PhotoSerializer(many=True, default=[Photo(**PLACEHOLDER_PHOTO)])
    geometry = GeometryField(precision=14)
    center = GeometryField(precision=14)
    length = serializers.DecimalField(None, 0)
    likes = serializers.SerializerMethodField()

    def get_likes(self, obj):
        return len(obj.likes.all())

    class Meta:
        model = Project
        fields = (
            'id',
            'url',
            'project_key',
            'title',
            'description',
            'short_description',
            'category',
            'street_name',
            'borough',
            'side',
            'costs',
            'draft_submitted',
            'construction_started',
            'construction_completed',
            'construction_completed_date',
            'phase',
            'responsible',
            'external_url',
            'cross_section',
            'faq',
            'geometry',
            'center',
            'length',
            'photos',
            'likes',
        )


class SectionDetailsSerializer(serializers.ModelSerializer):
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
        model = SectionDetails
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


class SectionSerializer(serializers.HyperlinkedModelSerializer):
    geometry = GeometryField(precision=14)
    details = SectionDetailsSerializer(many=True)

    class Meta:
        model = Section
        fields = (
            'url',
            'street_name',
            'suffix',
            'borough',
            'street_category',
            'geometry',
            'details',
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


class ReportDetailsField(serializers.Field):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        repr = {'subject': value.subject}
        if value.subject == Report.SUBJECT_BIKE_STANDS:
            repr.update(
                {
                    'number': value.bikestands.number,
                    'fee_acceptable': value.bikestands.fee_acceptable,
                }
            )
        return repr

    def to_internal_value(self, data):
        return data


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    details = ReportDetailsField()
    geometry = GeometryField(precision=14)
    likes = serializers.SerializerMethodField()
    liked_by_user = serializers.SerializerMethodField()
    photo = PhotoSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(
        many=False,
        queryset=get_user_model().objects.all(),
        required=False,
        write_only=True,
    )

    def get_likes(self, obj):
        return obj.likes.count()

    def get_liked_by_user(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.likes.filter(user=user).count() > 0
        else:
            return False

    def create(self, validated_data):
        photos_data = validated_data.pop('photo', [])
        details = validated_data.pop('details', {})
        if details['subject'] == Report.SUBJECT_BIKE_STANDS:
            validated_data.update(details)
            report = BikeStands.objects.create(**validated_data).report_ptr
        else:
            report = Report.objects.create(
                subject=validated_data['details']['subject'], **validated_data
            )
        for photo_data in photos_data:
            Photo.objects.create(content_object=report, **photo_data)
        return report

    def to_internal_value(self, data):
        if 'photo' in data:
            data['photo'] = [{'src': data['photo']}]
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['photo'] = next(iter(data['photo']), None)
        return data

    class Meta:
        model = Report
        fields = (
            'address',
            'created_date',
            'description',
            'details',
            'geometry',
            'id',
            'likes',
            'liked_by_user',
            'modified_date',
            'photo',
            'status',
            'status_reason',
            'url',
            'user',
        )


class PlaystreetSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaystreetSignup
        fields = [
            'campaign',
            'street',
            'first_name',
            'last_name',
            'email',
            'tos_accepted',
            'captain',
            'message',
        ]


class GastroSignupSerializer(serializers.ModelSerializer):
    geometry = GeometryField(precision=14)

    class Meta:
        model = GastroSignup
        fields = [
            'campaign',
            'shop_name',
            'first_name',
            'last_name',
            'category',
            'email',
            'address',
            'geometry',
            'shopfront_length',
            'opening_hours',
            'tos_accepted',
            'status',
        ]

        read_only_fields = ['campaign']


class GastroRegistrationSerializer(serializers.ModelSerializer):
    geometry = GeometryField(precision=14)
    area = GeometryField(precision=14, required=False, allow_null=True, default=None)

    class Meta:
        model = GastroSignup
        fields = [
            'campaign',
            'shop_name',
            'first_name',
            'last_name',
            'category',
            'email',
            'phone',
            'usage',
            'address',
            'geometry',
            'area',
            'shopfront_length',
            'opening_hours',
            'tos_accepted',
            'agreement_accepted',
            'status',
            'regulation',
            'application_received',
            'application_decided',
        ]

        read_only_fields = [
            'regulation',
            'campaign',
            'certificate',
            'application_received',
            'application_decided',
        ]


class GastroCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GastroSignup
        fields = ['certificate']
