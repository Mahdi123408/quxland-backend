from django.contrib import admin
from files.models import *


@admin.register(Files)
class FilesAdmin(admin.ModelAdmin):
    list_display = ['file', 'author', 'alt', 'is_public', 'is_active']
    list_editable = ['is_public', 'is_active']
