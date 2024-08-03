from django.contrib import admin
from setting.models import *


@admin.register(Rule)
class FilesAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'short_desc', 'is_active', 'created_at', 'updated_at']
    list_editable = ['is_active']
