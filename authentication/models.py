import datetime
from core.settings import COUNT_CLAIM_REFERRALS_POINTS, EXPIRED_FORGOT_KEY
from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class CustomUser(models.Model):
    username = models.CharField(max_length=100, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    password = models.CharField(max_length=100, db_index=True)
    phone = models.CharField(max_length=100, unique=True)
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, default='normal')
    diamond = models.IntegerField(default=0)
    wallet_address = models.CharField(max_length=200, unique=True, null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)
    rating = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    cover_url = models.ImageField(upload_to='covers', null=True, blank=True)
    avatar_url = models.ImageField(upload_to='avatars', null=True, blank=True)
    telegram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    instagram_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    points = models.IntegerField(default=0)
    strike = models.IntegerField(default=0)
    last_referral_claimed = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    super_verified = models.BooleanField(default=False)
    super_verify_video = models.FileField(upload_to='super_verify_videos', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.username} - {self.full_name}'

    class Meta:
        verbose_name = 'CustomUser'
        verbose_name_plural = 'CustomUsers'

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        if self.strike >= 3:
            self.is_active = False

        user_invited = Referral.objects.filter(user_id=self.id).first()
        if user_invited:
            if self.is_active and self.verified:
                user_invited.is_active = True
                user_invited.save()
                from_user = CustomUser.objects.filter(id=user_invited.from_user.id).first()
                refs = Referral.objects.filter(from_user_id=from_user.id, is_active=True)
                if refs:
                    len_rfs = len(refs)
                else:
                    len_rfs = 0
                if str(len_rfs) in COUNT_CLAIM_REFERRALS_POINTS.keys() and len_rfs > from_user.last_referral_claimed:
                    from_user.last_referral_claimed = len_rfs
                    from_user.points += COUNT_CLAIM_REFERRALS_POINTS[f'{len_rfs}']
                    from_user.save()
            else:
                user_invited.is_active = False
                user_invited.save()
        user_sms = SmsUserVerify.objects.filter(user_id=self.id).first()
        if user_sms:
            if self.is_active and self.verified:
                user_sms.delete()
        super(CustomUser, self).save(*args, **kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'diamond': self.diamond,
            'rating': self.rating,
            'level': self.level,
            'avatar_url': self.avatar_url.url if self.avatar_url else None,
            'cover_url': self.cover_url.url if self.cover_url else None,
            'telegram_id': self.telegram_id,
            'instagram_id': self.instagram_id,
            'points': self.points,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }


# class Device(models.Model):
#     mac_address = models.CharField(max_length=30, unique=True, db_index=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')
#
#     def __str__(self):
#         return self.mac_address
#
#     class Meta:
#         verbose_name = 'Device'
#         verbose_name_plural = 'Devices'


class Rating(models.Model):
    rating = models.IntegerField(default=0)
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings')
    to_user = models.ForeignKey(CustomUser, related_name='ratings_to', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.from_user} -> {self.to_user}: {self.rating}'

    class Meta:
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'


class History(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='history')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user} - {self.title[:15]}'

    class Meta:
        verbose_name = 'History'
        verbose_name_plural = 'Histories'


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=200, default='normal-notif')
    show = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.title[:15]}'

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'


class Referral(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='invited_by')
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='referrals')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.from_user} -> {self.user}'

    class Meta:
        verbose_name = 'Referral'
        verbose_name_plural = 'Referrals'
        unique_together = (('user', 'from_user'),)


class AccessToken(models.Model):
    token = models.CharField(max_length=800, unique=True, db_index=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=2, default='at', editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='access_tokens')
    token_id = models.CharField(max_length=800, db_index=True)

    def __str__(self):
        return f'{self.user} - {self.token_type} - {self.expires_at}'

    class Meta:
        verbose_name = 'Access Token'
        verbose_name_plural = 'Access Tokens'
        unique_together = (('token_type', 'token', 'token_id'),)


class RefreshToken(models.Model):
    token = models.CharField(max_length=800, unique=True, db_index=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    token_type = models.CharField(max_length=2, default='rt', editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='refresh_tokens')
    token_id = models.CharField(max_length=800, db_index=True)

    def __str__(self):
        return f'{self.user} - {self.token_type} - {self.expires_at}'

    class Meta:
        verbose_name = 'Refresh Token'
        verbose_name_plural = 'Refresh Tokens'
        unique_together = (('token_type', 'token', 'token_id'),)


class SmsUserVerify(models.Model):
    sms_code = models.CharField(max_length=6)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='sms_user')
    created_at = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=50, unique=True)  # ادیتیبل باید فالس بشه
    last_send_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user} - {self.sms_code}'

    class Meta:
        verbose_name = 'Sms User'
        verbose_name_plural = 'Sms Users'

    def save(self, *args, **kwargs):
        print(datetime.datetime.now())
        super(SmsUserVerify, self).save(*args, **kwargs)


class ForgotKey(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='forgot_key')
    key = models.CharField(max_length=100, unique=True)
    last_send_sms = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} : {self.key}'

    class Meta:
        verbose_name = 'Forgot Key'
        verbose_name_plural = 'Forgot Keys'


@receiver(post_save, sender=ForgotKey)
def forgot_key_post_save(sender, instance, created, **kwargs):
    if created:
        now = timezone.now()
        expt = now + EXPIRED_FORGOT_KEY
        instance.expires_at = expt
        instance.last_send_sms = now
        instance.save()


class News(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
