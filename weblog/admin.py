from django.contrib import admin
from weblog.models import *


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'thumbnail', 'content', 'category', 'short_description', 'created_at', 'updated_at', 'published_at', 'is_active']
    list_editable = ['is_active']