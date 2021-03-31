from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from .models import EventPermit


class EventPermitSerializer(serializers.ModelSerializer):
    area = GeometryField(precision=14, required=False, allow_null=True, default=None)

    fields = [
        'email',
        'tos_accepted',
        'agreement_accepted',
        'followup_accepted',
        'category',
        'org_name',
        'first_name',
        'last_name',
        'phone',
        'address',
        'date',
        'setup_start',
        'event_start',
        'event_end',
        'teardown_end',
        'num_participants',
        'area_category',
        'area',
        'setup_sketch',
        'title',
        'description',
        'details',
        'insurance',
        'agreement',
        'public_benefit',
        'status',
        'application_received',
        'application_decided',
        'permit_start',
        'permit_end',
        'note',
        'area_park_name',
    ]

    read_only_fields = [
        'status',
        'application_received',
        'application_decided',
        'permit_start',
        'permit_end',
        'note',
        'area_park_name',
    ]

    class Meta:
        model = EventPermit

    def validate(self, values):
        """Validate that the given S3 key exists in current bucket"""
        s3 = boto3.resource('s3')

        fields = ['insurance', 'agreement']
        if self.initial_data.get('public_benefit') is not None:
            fields.push('public_benefit')
        if self.initial_data.get('setup_sketch') is not None:
            fields.push('setup_sketch')

        for field in fields:
            try:
                s3.Object(
                    settings.AWS_STORAGE_BUCKET_NAME,
                    self.initial_data.get(field),
                ).load()
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == "404":
                    raise serializers.ValidationError(f"Missing upload: {field}")
                raise
            except ValueError:
                if self.initial_data.get(field) is None:
                    raise serializers.ValidationError(f"Missing upload: {field}")
                raise
        return values


class EventPermitDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventPermit
        fields = ['insurance', 'agreement', 'public_benefit', 'setup_sketch']