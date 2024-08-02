from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta

from weblog.models import *


class ArticleViewSerializer(serializers.ModelSerializer):
    category_id = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'thumbnail', 'short_description', 'created_at', 'updated_at',
                  'category_id', 'published_at', 'is_active']

    def get_category_id(self, obj):
        return {
            'id': obj.category.id,
            'name': obj.category.name,
        }


class CategoryViewSerializer(serializers.ModelSerializer):
    article = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'article']

    def get_article(self, obj):
        now = timezone.now()
        serializer = ArticleViewSerializer(obj.articles.filter(published_at__lte=now), many=True)
        return serializer.data


class CreateArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'thumbnail', 'content', 'category', 'short_description', 'published_at']


class ArticleChangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['title', 'thumbnail', 'content', 'category', 'short_description', 'published_at', 'is_active']
