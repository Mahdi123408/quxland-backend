from django.db import models
from authentication.models import CustomUser
from core.settings import CLICK_COUNT_PER_TIME, TIME_CLAIM_DOREATION
from datetime import datetime, timedelta
from django.utils import timezone


class AccountUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='click_account')
    time_last_claim = models.DateTimeField()
    count_last_claim = models.IntegerField(default=0)
    levrage = models.IntegerField(default=1)
    amount_tank = models.IntegerField(default=400)

    def add_claim(self, count: int):
        last_claim = self.time_last_claim
        now = timezone.now()
        if (last_claim + TIME_CLAIM_DOREATION) < now:
            if (self.count_last_claim + count) <= (CLICK_COUNT_PER_TIME + self.amount_tank):
                self.user.points += (self.count_last_claim + count) * self.levrage
                self.count_last_claim = 0
                self.time_last_claim = now
                self.save()
                self.user.save()
                return True
            else:
                self.user.points += CLICK_COUNT_PER_TIME * self.levrage
                self.count_last_claim = 0
                self.time_last_claim = now
                self.save()
                self.user.save()
                return True
        else:
            if (self.count_last_claim + count) > (CLICK_COUNT_PER_TIME + self.amount_tank):
                return False
            else:
                self.count_last_claim += count
                self.save()
                return True

    def __str__(self):
        return f'{str(self.user)} - {self.levrage}: {self.count_last_claim} -> {self.time_last_claim}'

    class Meta:
        verbose_name = 'AccountUser'
        verbose_name_plural = 'AccountUsers'
