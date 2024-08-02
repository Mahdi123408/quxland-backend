import datetime
from django.utils import timezone
from jwt.exceptions import DecodeError, ExpiredSignatureError
from .creators import crate_random_code
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
import random
import jwt
import uuid
from core import settings
from core.settings import CUSTOM_ACCESS_TOKEN_NAME, INDEX_0_AUTHORIZATION, SMS_PANEL_API_KEY
from authentication.models import CustomUser, AccessToken, RefreshToken, SmsUserVerify, ForgotKey
from my_methods.validators import str_finder
from my_methods.creators import create_random_name
from rest_framework import status
from ippanel import Client
from ippanel import HTTPError, Error, ResponseCode


def send_sms(phone_number, txt):
    sms = Client(SMS_PANEL_API_KEY)

    try:
        pattern_values = {
            "key": txt,
        }

        message_id = sms.send_pattern(
            "yuakjom5eipaijy",  # pattern code
            "+9810004551235312	",  # originator
            phone_number,  # recipient
            pattern_values,  # pattern values
        )
    except Error as e:  # ippanel sms error
        return False
    except HTTPError as e:  # http error like network error, not found, ...
        return False
    if message_id:
        return True
    else:
        return False


def create_access_token(user_obj: CustomUser):
    data = {}
    token_id = str(uuid.uuid4())
    now = datetime.datetime.now()
    expt = (datetime.datetime.now() + settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME']).strftime('%Y-%m-%d %H:%M:%S')
    data['created'] = now.strftime('%Y-%m-%d %H:%M:%S')
    data['token_id'] = token_id
    data['expt'] = expt
    data['type'] = 'at'
    access_token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
    try:
        AccessToken.objects.create(
            token=access_token,
            user=user_obj,
            expires_at=data['expt'],
            token_id=token_id,
            created_at=data['created']
        )
    except ValidationError or ValueError or TypeError:
        return Response({'error': 'Error in create token'}, status=status.HTTP_204_NO_CONTENT)
    return access_token


def create_key():
    list_str_tokens = ['a', '1', '2', 'q', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g',
                       'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', '4', '4', 'n', '2', '7', 'n', 'm', '0', '1', '2',
                       '3', '4', '5', '6', '7', '8', '9', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S',
                       'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M']
    access_token = ''
    b = 1
    while b <= 40:
        access_token += list_str_tokens[random.randint(0, len(list_str_tokens) - 1)]
        b += 1
    return access_token


def create_refresh_token(user_obj: CustomUser):
    data = {}
    token_id = str(uuid.uuid4())
    now = datetime.datetime.now()
    expt = (datetime.datetime.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']).strftime('%Y-%m-%d %H:%M:%S')
    data['created'] = now.strftime('%Y-%m-%d %H:%M:%S')
    data['token_id'] = token_id
    data['expt'] = expt
    data['type'] = 'rt'
    refresh_token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
    try:
        RefreshToken.objects.create(
            token=refresh_token,
            user=user_obj,
            expires_at=data['expt'],
            token_id=token_id,
            created_at=data['created']
        )
    except ValidationError or ValueError or TypeError:
        return Response({'error': 'Error in create token'}, status=status.HTTP_204_NO_CONTENT)
    return refresh_token


def decode_token(token):
    token = str_finder(token, ' ')
    if token[0] == INDEX_0_AUTHORIZATION:
        token = token[1]
        decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    else:
        decoded_jwt = 's'

    return decoded_jwt


def authenticate_token(decoded_jwt, type_token, token):
    token = str_finder(token, ' ')
    if token[0] == INDEX_0_AUTHORIZATION:
        token = token[1]
    else:
        return False, status.HTTP_400_BAD_REQUEST
    try:
        created = decoded_jwt['created']
        token_id = decoded_jwt['token_id']
        expired = decoded_jwt['expt']
        type = decoded_jwt['type']
    except KeyError:
        return False, status.HTTP_400_BAD_REQUEST
    now = datetime.datetime.now()
    try:
        expired = datetime.datetime.strptime(expired, '%Y-%m-%d %H:%M:%S')
        created = datetime.datetime.strptime(created, '%Y-%m-%d %H:%M:%S')
    except ValueError or TypeError:
        return False, status.HTTP_400_BAD_REQUEST
    if expired < now:
        return 'retry'
    if type_token != type:
        return False, status.HTTP_400_BAD_REQUEST
    if type_token == 'at':
        token_check = AccessToken.objects.filter(token=token, token_id=token_id, created_at=created,
                                                 expires_at=expired).first()
    elif type_token == 'rt':
        token_check = RefreshToken.objects.filter(token=token, token_id=token_id, created_at=created,
                                                  expires_at=expired).first()
    else:
        return False, status.HTTP_400_BAD_REQUEST
    if token_check and token_check.user.is_active:
        return True, token_check.user, status.HTTP_200_OK, token_check
    else:
        return False, status.HTTP_400_BAD_REQUEST


def auth(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    if username and password:
        user = CustomUser.objects.filter(username__iexact=username, verified=True, is_active=True).first()
        if user:
            if user.check_password(password):
                return True, user
            else:
                return False, 'Wrong password'
    return False, None


def login_auth(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')
    if username and password:
        # user = CustomUser.objects.filter(username__iexact=username, is_active=True).first()
        # if not user:
        user = CustomUser.objects.filter(email__iexact=username, is_active=True).first()
        if user:
            if user.check_password(password):
                if user.verified:
                    return True, user, False
                else:
                    sms_chek = SmsUserVerify.objects.filter(user=user).first()
                    if sms_chek:
                        return False, 'not verified give me sms code', sms_chek.key, user
                    else:
                        sms = send_sms_code(user)
                        if sms[0]:
                            return True, user, sms[1], user
                        else:
                            return False, "send sms error"

            else:
                return False, 'Wrong password'
    return False, False


def check_login(request):
    access_token = request.headers.get(CUSTOM_ACCESS_TOKEN_NAME)
    if access_token:
        try:
            try:
                decoded_jwt = decode_token(access_token)
            except ExpiredSignatureError:
                return False, "Invalid token"
            check = authenticate_token(decoded_jwt, 'at', access_token)
        except DecodeError or TypeError or ExpiredSignatureError:
            return False, "Invalid token"
        if check[0] == True:
            return True, check[1]
        elif check == 'retry':
            return False, "Token expired"
        else:
            return False, check[1]
    else:
        return False, "Access Token Required"


def send_sms_code(user, type_sms=None):
    if not type_sms:
        check = SmsUserVerify.objects.filter(user=user).first()
        if check:
            now = timezone.now()
            expt = check.last_send_at + settings.SMS_CODE_LIFETIME
            death_time = check.created_at + settings.SMS_CODE_DEATHTIME
            if expt < now:
                if death_time < now:
                    check.delete()
                    return False, 'Death time'
                sms_code = crate_random_code(6)
                key = create_key()
                check.sms_code = sms_code
                check.key = key
                check.save()
                sms = Client(SMS_PANEL_API_KEY)
                try:
                    pattern_values = {
                        "code": sms_code,
                    }

                    message_id = sms.send_pattern(
                        "cyi04e9ps7be4l4",  # pattern code
                        "+9810004551235312	",  # originator
                        check.user.phone,  # recipient
                        pattern_values,  # pattern values
                    )
                except Error as e:  # ippanel sms error
                    return False, 'error'
                except HTTPError as e:  # http error like network error, not found, ...
                    return False, 'error'
                if message_id:
                    return True, key
                else:
                    return False, 'error'

            else:
                return False, 'wait'
        else:
            sms_code = crate_random_code(6)
            key = create_key()
            if SmsUserVerify.objects.create(sms_code=sms_code, user=user, key=key):
                sms = Client(SMS_PANEL_API_KEY)
                try:
                    pattern_values = {
                        "code": sms_code,
                    }

                    message_id = sms.send_pattern(
                        "cyi04e9ps7be4l4",  # pattern code
                        "+9810004551235312	",  # originator
                        user.phone,  # recipient
                        pattern_values,  # pattern values
                    )
                except Error as e:  # ippanel sms error
                    return False, 'error'
                except HTTPError as e:  # http error like network error, not found, ...
                    return False, 'error'
                if message_id:
                    return True, key
                else:
                    return False, 'error'
            else:
                return False, 'error'
    elif type_sms == 'forgot':
        forgot_key = ForgotKey.objects.filter(user=user).first()
        if not forgot_key:
            key = create_random_name(settings.LEN_FORGOT_KEY)
            if send_sms(user.phone, key):
                forgot_key = ForgotKey.objects.create(key=key, user=user)
                return True, forgot_key
            else:
                return False, 'error'
        else:
            now = timezone.now()
            expt = forgot_key.last_send_sms + settings.SMS_CODE_LIFETIME
            death_time = forgot_key.expires_at
            if death_time < now:
                key = create_random_name(settings.LEN_FORGOT_KEY)
                if send_sms(user.phone, key):
                    forgot_key.key = key
                    forgot_key.last_send_sms = timezone.now()
                    forgot_key.created_at = timezone.now()
                    forgot_key.expires_at = timezone.now() + settings.EXPIRED_FORGOT_KEY
                    forgot_key.save()
                    return True, forgot_key
                else:
                    return False, 'error'
            elif expt < now:
                if send_sms(user.phone, forgot_key.key):
                    forgot_key.last_send_sms = timezone.now()
                    forgot_key.save()
                    return True, forgot_key
                else:
                    return False, 'error'
            else:
                now = timezone.now()
                expt = forgot_key.last_send_sms + settings.SMS_CODE_LIFETIME
                can_send = expt - now
                return False, 'wait', can_send
