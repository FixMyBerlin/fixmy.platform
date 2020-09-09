from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from fixmyapp.models import Photo
from fixmyapp.serializers import PhotoSerializer
from .models import BikeStands, Report


PLACEHOLDER_PHOTO = {
    'copyright': 'Photo by Anthony Ginsbrook',
    'src': 'photos/Platzhalter_anthony-ginsbrook-225252-unsplash.jpg',
}


ANOTHER_PLACEHOLDER_PHOTO = {
    'copyright': 'Photo by Emil Bruckner',
    'src': 'photos/emil-bruckner-532523-unsplash.jpg',
}


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
