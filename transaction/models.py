from django.db import models

from authentication.models import CustomUser


class Wallet(models.Model):
    wallet_name = models.CharField(max_length=100)
    wallet_address = models.CharField(max_length=250)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.wallet_name


class DiamondPackage(models.Model):
    title = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='images/diamond_thumbnail/')
    description = models.TextField()
    value = models.IntegerField()
    price = models.FloatField()
    type = models.CharField(max_length=100)
    discount = models.FloatField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Transaction(models.Model):
    tx_hash = models.CharField(max_length=66, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField()
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    for_buy = models.ForeignKey(DiamondPackage, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user}: {self.amount} -> {self.status}'
