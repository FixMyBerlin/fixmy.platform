from rest_framework import serializers
from .models import Rating, Survey


class RatingSerializer(serializers.ModelSerializer):
    scene_id = serializers.StringRelatedField(source='scene')

    class Meta:
        model = Rating
        fields = ('scene_id', 'duration', 'rating')


class SurveySerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source='id')
    created = serializers.DateTimeField(source='created_date', read_only=True)
    last_scene_id = serializers.SerializerMethodField()
    ratings = RatingSerializer(many=True, read_only=True)

    def get_last_scene_id(self, obj):
        return str(obj.ratings.last().scene) if obj.ratings.last() else None

    class Meta:
        model = Survey
        fields = (
            'session_id',
            'project',
            'profile',
            'created',
            'last_scene_id',
            'ratings'
        )
