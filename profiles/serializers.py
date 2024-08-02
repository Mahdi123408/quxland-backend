from rest_framework import serializers
from authentication.models import CustomUser, History, News


class ProfileChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'telegram_id', 'instagram_id', 'wallet_address', 'cover_url', 'avatar_url']


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['title', 'description', 'location', 'type', 'created_at']


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['text']
