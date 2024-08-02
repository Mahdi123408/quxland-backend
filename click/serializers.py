from rest_framework import serializers
from authentication.models import CustomUser


class UserAndClickSerializer(serializers.ModelSerializer):
    ref = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'full_name', 'point', 'profile', 'ref', 'level')

    def get_ref(self, obj):
        l = []
        if obj.referrals:
            referrals = obj.referrals.filter(is_active=True)
            for ref in referrals:
                l.append(
                    {
                        'username': ref.username,
                        'points': ref.points,
                        'full_name': ref.full_name,
                    }
                )
            return l
        else:
            return None

    def get_profile(self, obj):
        if obj.avatar_url:
            return obj.avatar_url.url
        else:
            return None

    def get_level(self, obj):
        return obj.click_account.levrage

    def get_point(self, obj):
        return (obj.click_account.count_last_claim * obj.click_account.levrage) + obj.points
