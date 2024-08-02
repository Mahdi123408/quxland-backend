from django.utils import timezone

from task.models import Task

from authentication.models import Referral

import re

import requests

from core.settings import BNB_API_KEY, WALLET


def check_task(query_set: Task):
    now = timezone.now()
    change = False
    for task in query_set:
        if task.expires_at < now:
            task.expired = True
            task.save()
            change = True
    if change:
        return Task.objects.all()
    else:
        return query_set


def check_daily_task(query_set):
    # now = timezone.now()
    # change = False
    # for task in query_set:
    #     if task.expires_at < now:
    #         task.expired = True
    #         task.save()
    #         change = True
    # if change:
    #     return DailyTask.objects.all()
    # else:
    #     return query_set
    ...


def validate_phone(phone_number):
    if len(phone_number) == 11 and phone_number[0] == "0":
        return phone_number
    elif len(phone_number) == 10 and phone_number[0] == "9":
        return '0' + phone_number
    else:
        return phone_number


def str_finder(text, chr):
    x = []
    y = ''
    i = 0
    b = len(text)
    for ch in text:
        if ch == chr:
            x.append(y)
            y = ''
            i += 1
        elif i == (b - 1):
            y += ch
            i += 1
            x.append(y)
            break
        else:
            y += ch
            i += 1
    return x


def referral_len(user_id):
    refrrals = Referral.objects.filter(is_active=True, from_user_id=user_id)
    if refrrals:
        return len(refrrals)
    else:
        return 0


def validate_file_name(file_name):
    new_file_name = ''
    for char in file_name:
        if char not in [' ', '(', ')']:
            new_file_name += char
    return new_file_name


def validate_user_wallet(wallet):
    if not wallet:
        return False
    if len(wallet) != 42:
        return False
    if not wallet.startswith("0x"):
        return False
    if not re.match(r"^0x[a-fA-F0-9]{40}$", wallet):
        return False
    return True


def get_transaction_by_address(address):
    url = 'https://api-testnet.bscscan.com/api'
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': address,
        'startblock': '0',
        'page': '1',
        'offset': '500',
        'endblock': '99999999',
        'sort': 'desc',
        'apikey': BNB_API_KEY
    }
    response = requests.get(url, params=params)
    data1 = response.json()
    params = {
        'module': 'account',
        'action': 'txlist',
        'address': WALLET,
        'startblock': '0',
        'page': '1',
        'offset': '500',
        'endblock': '99999999',
        'sort': 'desc',
        'apikey': BNB_API_KEY
    }
    response = requests.get(url, params=params)
    data2 = response.json()
    return data2, data1


def find_transaction(tx_hash, results: list):
    if results:
        b = 0
        while b < len(results):
            if results[b]['hash'] == tx_hash:
                return results[b]
            b += 1
        return None
    else:
        return None


def get_bnb_price():
    url = 'https://api.bscscan.com/api'
    params = {
        'module': 'stats',
        'action': 'bnbprice',
        'apikey': BNB_API_KEY
    }
    response = requests.get(url, params=params)
    data = response.json()
    if data['status'] == '1':
        return float(data['result']['ethusd'])
    return None
