from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()

    class Meta:
        model = Profile
        fields = '__all__'
