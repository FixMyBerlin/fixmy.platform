import boto3
import botocore
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_extra_fields.fields import HybridImageField
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from .models import (
    GastroSignup,
    Photo,
    PlaystreetSignup,
    Profile,
    Project,
    Question,
    Section,
    SectionAccidents,
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


class SectionAccidentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionAccidents
        fields = [
            'killed',
            'severely_injured',
            'slightly_injured',
            'side',
            'source',
            'risk_level',
        ]


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
    accidents = SectionAccidentsSerializer(many=True)

    class Meta:
        model = Section
        fields = (
            'accidents',
            'borough',
            'details',
            'geometry',
            'is_road',
            'street_category',
            'street_name',
            'suffix',
            'url',
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
            'followup_accepted',
            'status',
        ]


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
            'followup_accepted',
            'agreement_accepted',
            'status',
            'regulation',
            'application_received',
            'application_decided',
            'permit_start',
            'permit_end',
            'renewal_application',
            'note',
        ]

        read_only_fields = [
            'regulation',
            'certificate',
            'application_received',
            'application_decided',
            'permit_start',
            'permit_end',
            'renewal_application',
            'note',
        ]


class GastroDirectRegistrationSerializer(GastroRegistrationSerializer):
    def validate(self, values):
        """Validate that the given S3 key exists in current bucket"""
        s3 = boto3.resource('s3')
        try:
            s3.Object(
                settings.AWS_STORAGE_BUCKET_NAME, self.initial_data.get('certificateS3')
            ).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                raise serializers.ValidationError(_('Please upload a certificate'))
            raise
        except ValueError:
            if self.initial_data.get('certificateS3') is None:
                raise serializers.ValidationError(_('Please upload a certificate'))
            raise
        return values


class GastroCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = GastroSignup
        fields = ['certificate']
