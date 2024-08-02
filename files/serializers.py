from rest_framework import serializers
from files.models import *


class FileViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Files
        fields = ['id', 'file', 'alt', 'user', 'is_public', 'is_active']

    def get_user(self, obj):
        if obj.author:
            return obj.author.to_dict()
        else:
            return None


class FileCreateSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(FileCreateSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Files
        fields = ['file', 'alt']

    def create(self, validated_data):
        if self.user and self.user.role == 'superuser':
            validated_data['author'] = self.user
            return super(FileCreateSerializer, self).create(validated_data)
        else:
            raise serializers.ValidationError({'author': 'You must be logged in!'})
