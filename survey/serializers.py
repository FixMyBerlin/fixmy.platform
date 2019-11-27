from rest_framework import serializers
from .models import Rating, Session


class RatingSerializer(serializers.ModelSerializer):
    scene_id = serializers.StringRelatedField(source='scene')

    class Meta:
        model = Rating
        fields = ('scene_id', 'duration', 'rating')


class SessionSerializer(serializers.ModelSerializer):
    session_id = serializers.UUIDField(source='id')
    created = serializers.DateTimeField(source='created_date', read_only=True)
    stopped_at_scene_id = serializers.SerializerMethodField()
    ratings = serializers.SerializerMethodField()

    def get_stopped_at_scene_id(self, obj):
        is_partial = (
            any(r.rating is not None for r in obj.ratings.all()) and
            any(r.rating is None for r in obj.ratings.all())
        )
        if is_partial:
            missing_scenes = [
                r.scene for r in obj.ratings.all() if r.rating is None
            ]
            return str(missing_scenes[0])

    def get_ratings(self, obj):
        ratings = [r for r in obj.ratings.all() if r.rating is not None]
        return RatingSerializer(ratings, many=True, read_only=True).data

    class Meta:
        model = Session
        fields = (
            'session_id',
            'project',
            'profile',
            'created',
            'stopped_at_scene_id',
            'ratings'
        )
