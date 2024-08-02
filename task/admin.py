from django.contrib import admin
from .models import *


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'created_at', 'updated_at', 'expires_at', 'expired', 'point_value',
                    'image_url', 'is_active']
    list_editable = ['is_active']


@admin.register(CompletedTask)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'created_at']


# @admin.register(DailyTask)
# class DailyTaskAdmin(admin.ModelAdmin):
#     list_display = ['title', 'created_at', 'expires_at', 'expired', 'point_value', 'is_active']
#     list_editable = ['is_active']


@admin.register(DailyCompletedTask)
class DailyCompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'count']
