from django.contrib import admin
from transaction.models import *


@admin.register(DiamondPackage)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'description', 'value', 'price', 'discount',
                    'is_active',
                    'updated_at']
    list_editable = ['is_active']


@admin.register(Transaction)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'tx_hash', 'user', 'amount', 'status', 'created_at', 'updated_at', 'for_buy']


@admin.register(Wallet)
class CompletedTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet_name', 'wallet_address', 'is_active']
    list_editable = ['is_active']
