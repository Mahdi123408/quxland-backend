from rest_framework import serializers
from .models import CustomUser, Referral, SmsUserVerify, News, History
from my_methods.validators import validate_phone
from my_methods.auth import send_sms_code
from django.core.exceptions import ValidationError
import re


class UserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'full_name', 'phone', 'role', 'diamond', 'wallet_address', 'rating', 'level',
                  'cover_url', 'avatar_url', 'telegram_id', 'instagram_id', 'points', 'created_at', 'updated_at']


class ReferralViewSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Referral
        fields = ['username', 'full_name', 'avatar_url', 'created_at']

    def get_username(self, obj):
        return obj.user.username

    def get_full_name(self, obj):
        return obj.user.full_name

    def get_avatar_url(self, obj):
        if obj.user.avatar_url:
            return obj.user.avatar_url.url


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    id_referral = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'full_name', 'phone', 'id_referral']

    def validate_username(self, value):
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError("Username can only contain letters, numbers, and underscores.")
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a valid email address.")
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[@!_.#]', value):
            raise serializers.ValidationError("Password must contain at least one special character (@, !, _ , # or .).")
        return value

    def validate_phone(self, value):
        print(value)
        value = validate_phone(value)
        if not re.match(r'^(09|9)\d{9}$', value):
            raise serializers.ValidationError("Phone number must start with 09 or 9 and be 10 or 11 digits long.")
        if CustomUser.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Phone number is already registered.")
        return value

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        referral_id = validated_data.pop('id_referral', None)
        user = CustomUser.objects.create(**validated_data)
        user.set_password(user.password)
        if referral_id:
            from_user = CustomUser.objects.filter(username=referral_id).first()
            if from_user:
                Referral.objects.create(user=user, from_user=from_user, is_active=False)
                description = f'کاربر {user.username}، دعوت کاربر {from_user.username} را پذیرفت.'
                News.objects.create(
                    text=description,
                )
                History.objects.create(
                    user=from_user,
                    title=f'پذیرفتن دعوت شما توسط کاربر {user.username}',
                    description=description + '\nتوجه داشته باشید که تا زمانی که کاربر شماره خود را تایید نکند دعوت شما کامل نشده است .',
                    location='Referral',
                    type='accept'
                )
        sms = send_sms_code(user)
        if sms[0]:
            ...
        elif sms[1] == 'Death time':
            sms = send_sms_code(user)
            if sms[0]:
                ...
            else:
                raise ValidationError("send sms error")
        else:
            raise ValidationError("send sms error")
        return user, sms[1]
