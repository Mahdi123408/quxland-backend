from django.contrib import admin
from click.models import *


@admin.register(AccountUser)
class AccountUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'time_last_claim', 'count_last_claim', 'levrage', 'amount_tank')
