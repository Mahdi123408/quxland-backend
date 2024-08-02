from django.contrib import admin
from authentication.models import *


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email', 'encripted_password', 'full_name', 'role', 'diamond', 'rating',
                    'level', 'points',
                    'is_active', 'verified']

    def encripted_password(self, obj):
        return obj.password[:5] + ' ... .'


# @admin.register(Device)
# class DeviceAdmin(admin.ModelAdmin):
#     list_display = ['mac_address', 'created_at', 'updated_at', 'user']


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_user', 'created_at', 'updated_at', 'is_active']
    list_editable = ['is_active']


@admin.register(AccessToken)
class AccessTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'expires_at', 'token_type', 'token_id']


@admin.register(RefreshToken)
class RefreshTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'expires_at', 'token_type', 'token_id']


@admin.register(SmsUserVerify)
class SmsUserVerifyAdmin(admin.ModelAdmin):
    list_display = ['user', 'sms_code', 'created_at']


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'description', 'type', 'location', 'created_at']
    search_fields = ['title', 'location']
    list_filter = ['type']


@admin.register(ForgotKey)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'expires_at', 'created_at', 'last_send_sms']


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['text', 'created_at']
