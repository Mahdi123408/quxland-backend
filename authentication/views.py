from datetime import datetime
from django.http import HttpRequest
from jwt import DecodeError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from my_methods.auth import auth, create_access_token, create_refresh_token, authenticate_token, decode_token, \
    send_sms_code, login_auth
from my_methods.creators import create_random_name
from rest_framework.views import APIView
from authentication.serializers import UserViewSerializer, CustomUserCreateSerializer
from authentication.models import *
from core import settings
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME, LEN_FORGOT_KEY
from rest_framework_simplejwt.tokens import AccessToken as AccessTokenMethode, RefreshToken as RefreshTokenMethode
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from jwt.exceptions import ExpiredSignatureError


class UserAPIView(APIView):

    @swagger_auto_schema(
        operation_description="برگرداندن اطلاعات کاربر .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و اکسس توکن کاربر\nاگه Access Token Required اومد اطلاعات درست ارسال نشده\nاگه Invalid token اومد توکن اشتباهه\nاگه Token expired اومد توکن منقضی شده",
                examples={
                    "application/json": "Access Token Required"
                }
            ),
            200:
                openapi.Response(
                    description="اطلاعات یوزر . ",
                    examples={
                        "application/json": {
                            "user": {
                                "username": "mahdi_abbasi_from_api",
                                "email": "abasimahdi253@gmail.com",
                                "full_name": "مهدی عباسی",
                                "phone": "09055601501",
                                "role": "normal",
                                "ivt_balance": 0,
                                "wallet_address": "ohvajoi",
                                "rating": 0,
                                "level": 0,
                                "cover_url": None,
                                "avatar_url": None,
                                "telegram_id": None,
                                "instagram_id": None,
                                "points": 0,
                                "created_at": "2024-06-12T03:39:25.591550+03:30",
                                "updated_at": "2024-06-12T04:04:27.128266+03:30"
                            }
                        }
                    }

                )
        },
    )
    def get(self, request: HttpRequest):
        data = request.headers
        access_token = data.get(CUSTOM_ACCESS_TOKEN_NAME)
        if access_token:
            try:
                check = authenticate_token(decode_token(access_token), 'at', access_token)
            except DecodeError or TypeError:
                return Response('Invalid token', status=status.HTTP_400_BAD_REQUEST)
            if check[0] == True:
                try:
                    serializer = UserViewSerializer(check[1])
                    return Response(data={'user': serializer.data}, status=status.HTTP_200_OK)
                except TypeError or ValueError or AttributeError or KeyError:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            elif check == 'retry':
                return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):

    @swagger_auto_schema(
        operation_description="دادن نام کاربری و رمز و دریافت اکسس توکن و رفرش توکن .",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           default='mahdi_abbasi_from_api'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='رمز عبور', default='@Aa123456'),
            },
            required=['username', 'password']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در ورود کاربر",
                examples={
                    "application/json": "Login Failed"
                }
            ),
            200: openapi.Response(
                description="اکسس توکن و رفرش توکن . ",
                examples={
                    "application/json": {

                        'access': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkIjoiMjAyNC0wNi0xNCAxODowNDo1OSIsInRva2VuX2lkIjoiMjA1OWMwYzgtOWZhYy00M2JjLTlkYTMtODM2NTc0MmM3N2QxIiwiZXhwdCI6IjIwMjQtMDYtMTUgMTg6MDQ6NTkiLCJ0eXBlIjoiYXQifQ.CSaB2QABFXi4B-SALqHsUXuZpn2EydvGvTpdeMfMwr8",
                        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkIjoiMjAyNC0wNi0xNCAxODowNDo1OSIsInRva2VuX2lkIjoiNzZkYjI2ZTItNjdhYS00ZmYwLTlhOGQtYWQ2YzllOGQ2MjBmIiwiZXhwdCI6IjIwMjQtMDYtMTcgMTg6MDQ6NTkiLCJ0eXBlIjoicnQifQ.3g9sPymcpemDrMrRLfXKV7LfBLcCdwOFjNmXbnmiGeU"

                    }
                }

            ),
            201: openapi.Response(
                description="زمانی که کاربری که نام کاربری و رمز او را وارد کرده اید اکانت خود را وریفای نکرده باشد و کدی برای شماره او ارسال شده باشد کلید وریفای را به شما میدهد",
                examples={
                    "application/json": {"key": "EIZ1jcVqZmNfdIiEX5VrLcRmkcuOUucA4iz82mYV",
                                         "time": "2024-06-14T18:39:40.973550Z"}

                }
            ),
            204: openapi.Response(
                description="خطا در ارسال اس ام اس برای کاربر احراز هویت نشده .",
                examples={
                    "application/json": {
                        "error": "Your mobile number is not verified and I could not send the code. try again"
                    }
                }
            )
        },
    )
    def post(self, request):

        user = login_auth(request)
        if user[0] and user[2] == False:
            data = {
                'access': f'{create_access_token(user[1])}',
                'refresh': f'{create_refresh_token(user[1])}'
            }
            return Response(data, status=status.HTTP_200_OK)
        elif user[0] and user[2]:
            check = SmsUserVerify.objects.filter(key=user[2]).first()
            number = str(user[3].phone)
            return Response({
                "key": user[2],
                "number": number[:4] + '...' + number[8:],
                "time": check.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
            }, status=status.HTTP_201_CREATED)
        elif not user[0] and user[1] == 'Wrong password':
            return Response("Login Failed", status=status.HTTP_400_BAD_REQUEST)
        elif not user[0] and user[1] == 'send sms error':
            return Response({
                "error": "Your mobile number is not verified and I could not send the code. try again"
            }, status=status.HTTP_204_NO_CONTENT)
        elif not user[0] and user[1] == 'not verified give me sms code':
            check = SmsUserVerify.objects.filter(key=user[2]).first()
            number = str(user[3].phone)
            return Response({
                "key": user[2],
                "number": number[:4] + '...' + number[8:],
                "time": check.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response("Login Failed", status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenAPIView(APIView):

    @swagger_auto_schema(
        operation_description="دادن نام کاربری و رمز و دریافت اکسس توکن و رفرش توکن .",
        manual_parameters=[
            openapi.Parameter(
                'refresh',
                openapi.IN_HEADER,
                description="رفرش توکن کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در رفرش توکن",
                examples={
                    "application/json": "Invalid Token"
                }
            ),
            201: openapi.Response(
                description="برگشتن اکسس توکن",
                examples={
                    "application/json": {
                        'access-token': 'eysnvonojkjdnnfnu4th39th9hht83tt89whw98h04ht00h9',
                    }

                }
            )
        },
    )
    def get(self, request: HttpRequest):

        refresh_token = request.headers.get('refresh')
        if not refresh_token:
            return Response("Refresh Token Required", status=status.HTTP_400_BAD_REQUEST)
        try:
            check_refresh_token = authenticate_token(decode_token(refresh_token), 'rt', refresh_token)
        except DecodeError:
            return Response("Invalid Token", status=status.HTTP_400_BAD_REQUEST)

        if check_refresh_token[0] == True:
            data = {
                'access-token': f'{create_access_token(check_refresh_token[1])}',
            }
            return Response(data, status=status.HTTP_201_CREATED)

        elif check_refresh_token == 'retry':
            return Response("Token Expired", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=check_refresh_token[1])


class RegisterAPIView(APIView):

    @swagger_auto_schema(
        operation_description="ثبت نام .",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           ),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='ایمیل',
                                        ),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='رمز عبور',
                                           ),
                'password2': openapi.Schema(type=openapi.TYPE_STRING, description='تکرار رمز عبور',
                                            ),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='نام کامل',
                                            ),
                'phone': openapi.Schema(type=openapi.TYPE_STRING, description='شماه همراه'),
                'id_referral': openapi.Schema(type=openapi.TYPE_STRING, description='یوزر نیم کاربری که دعوت داده'),
            },
            required=['username', 'email', 'password', 'password2', 'full_name', 'phone']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در ثبت نام کاربر",
                examples={
                    "application/json": "Register Failed"
                }
            ),
            201: openapi.Response(
                description="ثبت موفق اطلاعات کاربر و برگرداندن اطلاعات کاربر به همراه کلید و تایم وریفای",
                examples={
                    "application/json": {
                        "user": {
                            "username": "mehdi_abbasid",
                            "email": "abasimahdi2445@gmail.com",
                            "password": "@Aa123456",
                            "password2": "@Aa123456",
                            "full_name": "میتی عبوسی",
                            "phone": "09132895065"
                        },
                        "key": "EIZ1jcVqZmNfdIiEX5VrLcRmkcuOUucA4iz82mYV",
                        "time": "2024-06-14T18:39:40.973550Z"
                    }

                }
            )
        },
    )
    def post(self, request):
        data = request.data
        serializer = CustomUserCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            sms_sended = SmsUserVerify.objects.filter(key=user[1]).first()
            return Response(data={
                'user': serializer.validated_data,
                'key': user[1],
                'time': sms_sended.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(data="Register Failed", status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneNumberAPIView(APIView):

    @swagger_auto_schema(
        operation_description="دادن کلید و گرفتن اطلاعات مربوط بهش مثل شماره شخص و مورد اعتبار بودنش و یا تایمی میتونه دوباره کد بفرسته .",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_HEADER,
                description="کلید کاربر برای تایید شمارش",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در کلید",
                examples={
                    "application/json": "not found key"
                }
            ),
            302: openapi.Response(
                description="برگشتن اطلاعات کلید",
                examples={
                    "application/json": {'number': '0905....456',
                                         'time': '2024-06-14T18:39:40.973550Z'
                                         }
                }
            )
        },
    )
    def get(self, request: HttpRequest):
        data = request.headers
        key = data.get('key')
        if not key:
            return Response("key is required", status=status.HTTP_400_BAD_REQUEST)
        sms_sended = SmsUserVerify.objects.filter(key=key).first()
        if sms_sended:
            if sms_sended.user.verified:
                sms_sended.delete()
                return Response("not found key", status=status.HTTP_400_BAD_REQUEST)
            number = f'{sms_sended.user.phone[:5]}...{sms_sended.user.phone[8:]}'
            return Response(data={'number': number,
                                  'time': sms_sended.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3,
                                                                                                           minutes=30)
                                  }, status=status.HTTP_302_FOUND)
        else:
            return Response("not found key", status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="دادن کلید و کد تایید برای تایید شماره کاربر .",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_HEADER,
                description="کلید کاربر برای تایید شمارش",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'code',
                openapi.IN_HEADER,
                description="کد کاربر برای تایید شمارش",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در کلید یا کد",
                examples={
                    "application/json": "not found key"
                }
            ),
            200: openapi.Response(
                description="تایید شماره همراه و اکانت"
            )
        },
    )
    def put(self, request: HttpRequest):
        data = request.headers
        key = data.get('key')
        if not key:
            return Response("key is required", status=status.HTTP_400_BAD_REQUEST)
        sms_sended = SmsUserVerify.objects.filter(key=key).first()
        if not sms_sended:
            return Response("not found key", status=status.HTTP_400_BAD_REQUEST)
        if sms_sended.user.verified:
            sms_sended.delete()
            return Response("not found key", status=status.HTTP_400_BAD_REQUEST)
        code = data.get('code')
        if not code:
            return Response("code is required", status=status.HTTP_400_BAD_REQUEST)
        if sms_sended.sms_code == code:
            sms_sended.user.verified = True
            sms_sended.user.save()
            referral = Referral.objects.filter(user=sms_sended.user).first()
            if referral:
                referral.is_active = True
                referral.save()
            sms_sended.delete()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response("code is invalid", status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="دادن کلید و ارسال مجدد کد .",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_HEADER,
                description="کلید کاربر برای ارسال مجدد",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            400: openapi.Response(
                description="مشکلی در کلید :\nاگه wait برگشت یعنی هنوز نمیتونه کد بفرسته\nاگه error برگردوند یعنی یه مشکلی پیش اومده و کد ارسال نشده",
                examples={
                    "application/json": "wait"
                }
            ),
            200: openapi.Response(
                description="ارسال مجدد با موفقیت انجام شد",
                examples={
                    "application/json": {"key": "EIZ1jcVqZmNfdIiEX5VrLcRmkcuOUucA4iz82mYV",
                                         "time": "2024-06-14T18:39:40.973550Z"
                                         }
                }
            )
        },
    )
    def post(self, request: HttpRequest):
        data = request.headers
        key = data.get('key')
        if not key:
            return Response("key is required", status=status.HTTP_400_BAD_REQUEST)
        sms_sended = SmsUserVerify.objects.filter(key=key).first()
        if not sms_sended:
            return Response("not found key", status=status.HTTP_400_BAD_REQUEST)
        sms = send_sms_code(sms_sended.user)
        if sms[0]:
            sms_sended = SmsUserVerify.objects.filter(key=sms[1]).first()
            return Response(
                {
                    'key': sms[1],
                    'time': sms_sended.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
                }
                , status=status.HTTP_200_OK)
        elif sms[1] == 'Death time':
            sms = send_sms_code(sms_sended.user)
            if sms[0]:
                sms_sended = SmsUserVerify.objects.filter(key=sms[1]).first()
                return Response(
                    {
                        'key': sms[1],
                        'time': sms_sended.last_send_at + settings.SMS_CODE_LIFETIME + timedelta(hours=3, minutes=30)
                    }
                    , status=status.HTTP_200_OK)
            elif sms[1] == 'wait':
                return Response("wait", status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response("error", status=status.HTTP_400_BAD_REQUEST)
        elif sms[1] == 'wait':
            return Response("wait", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="دادن کلید و حذف آن .",
        manual_parameters=[
            openapi.Parameter(
                'key',
                openapi.IN_HEADER,
                description="کلید کاربر برای تایید شمارش",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            400: openapi.Response(
                description="پیدا نشدن یا نفرستادن key",
                examples={
                    "application/json": "not found key"
                }
            ),
            204: openapi.Response(
                description="حذف شدن کلید"
            )
        },
    )
    def delete(self, request: HttpRequest):
        data = request.headers
        key = data.get('key')
        if not key:
            return Response("key is required", status=status.HTTP_400_BAD_REQUEST)
        sms_sended = SmsUserVerify.objects.filter(key=key).first()
        if not sms_sended:
            return Response("not found key", status=status.HTTP_400_BAD_REQUEST)
        sms_sended.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ValidateTokenView(APIView):
    @swagger_auto_schema(
        operation_description="اعتبار سنجی توکن.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='توکن',
                                        ),
                'token_type': openapi.Schema(type=openapi.TYPE_STRING, description='نوع توکن مثل access یا refresh',
                                             ),
            },
            required=['token', 'token_type']
        ),
        responses={
            200: openapi.Response(
                description="معتبر بودن توکن",
                examples={
                    "application/json": {
                        "valid": True,
                        "expires_at": "2024-06-16T15:43:12",
                    }
                }
            ),
            400: openapi.Response(
                description="مشکلی پیش اومده . ",
                examples={
                    "application/json": {
                        "valid": False,
                    }
                }
            ),
        },
    )
    def post(self, request):
        token_type = request.data.get('token_type')
        token = request.data.get('token')
        try:
            decoded_jwt = decode_token(token)
        except ExpiredSignatureError:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
        if not token_type or not token:
            return Response({'error': 'token_type and token are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if token_type == 'access':
            check_token = authenticate_token(decoded_jwt, 'at', token)
        elif token_type == 'refresh':
            check_token = authenticate_token(decoded_jwt, 'rt', token)
        else:
            return Response({'error': 'Invalid token_type. It must be either "access" or "refresh".'},
                            status=status.HTTP_400_BAD_REQUEST)

        if check_token[0]:
            return Response({'valid': True, 'expires_at': check_token[3].expires_at + timedelta(hours=3, minutes=30)})
        else:
            return Response({'valid': False}, status=status.HTTP_400_BAD_REQUEST)


class GetUserInfoView(APIView):
    def get(self, request, username):
        user = CustomUser.objects.filter(username__iexact=username, is_active=True).first()
        if user:
            return Response(data=user.to_dict(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ForgotPasswordView(APIView):

    @swagger_auto_schema(
        operation_description="ثبت درخواست فراموشی رمز عبور.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           ),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='ایمیل',
                                        ),
            },
            required=['username', 'email']
        ),
        responses={
            200: openapi.Response(
                description="درست بودن اطلاعات و ارسال شدن پیامک",
                examples={
                    "application/json": {
                        "expires_at": "2024-07-19T16:54:21.793988Z",
                        "can_request_after": "0:02:00"
                    }
                }
            ),
            400: openapi.Response(
                description="مشکلی در ارسال پیامک و یا نگذشتن از اعتبار پیام قبلی و یا ارسال نکردن فیلد های مورد نظر . ",
                examples={
                    "application/json": {
                        "can_request_after": "0:01:32.242099"
                    }
                }
            ),
            404: openapi.Response(
                description="اشتباه بودن اطلاعات و پیدا نشدن یوزر . ",
            ),
        },
    )
    def post(self, request):
        data = request.data
        if 'email' not in data or 'username' not in data:
            return Response({'error': 'email and username are required'}, status=status.HTTP_400_BAD_REQUEST)
        user = CustomUser.objects.filter(username__iexact=data['username'], email__iexact=data['email'],
                                         is_active=True).first()
        if not user:
            return Response(status=status.HTTP_404_NOT_FOUND)
        result = send_sms_code(user, 'forgot')
        if result[0]:
            now = timezone.now()
            data = {
                'expires_at': result[1].expires_at + timedelta(hours=3, minutes=30),
                'can_request_after': str(settings.SMS_CODE_LIFETIME)
            }
            return Response(data=data, status=status.HTTP_200_OK)
        elif result[1] == 'wait':
            return Response(data={'can_request_after': str(result[2])}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data='send_sms_error', status=status.HTTP_400_BAD_REQUEST)


class ForgotVerifyAPIView(APIView):
    @swagger_auto_schema(
        operation_description="اعتبار سنجی کلید بازیابی رمز عبور.",
        responses={
            200: openapi.Response(
                description="درست بودن کلید و برگرداندن یوزر نیم کاربری که قصد ویرایش پسور داره",
                examples={
                    "application/json": {
                        "username": "mahdi_abbasi"
                    }
                }
            ),
            404: openapi.Response(
                description="اشتباه بودن و یا منقضی شدن کلید . ",
            ),
        },
    )
    def get(self, request, key):
        forgot_key = ForgotKey.objects.filter(key=key).first()
        if not forgot_key:
            return Response(status=status.HTTP_404_NOT_FOUND)
        now = timezone.now()
        if forgot_key.expires_at < now:
            forgot_key.delete()
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(data={
            'username': f'{forgot_key.user.username}',
        })

    @swagger_auto_schema(
        operation_description="عوض کردن رمز عبور.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'password1': openapi.Schema(type=openapi.TYPE_STRING, description='رمز',
                                            ),
                'password2': openapi.Schema(type=openapi.TYPE_STRING, description='تکرار رمز',
                                            ),
            },
            required=['password1', 'password2']
        ),
        responses={
            200: openapi.Response(
                description="عوض شدن رمز"
            ),
            400: openapi.Response(
                description="ارسال نشدن و یا مساوی نبودن ورودی ها . ",
                examples={
                    "application/json": {
                        'error': 'password1 and password2 are required'
                    }
                }
            ),
            404: openapi.Response(
                description="اشتباه بودن کلید و پیدا نشدن یوزر . ",
            ),
        },
    )
    def put(self, request, key):
        forgot_key = ForgotKey.objects.filter(key=key).first()
        if not forgot_key:
            return Response(status=status.HTTP_404_NOT_FOUND)
        now = timezone.now()
        if forgot_key.expires_at < now:
            forgot_key.delete()
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = request.data
        if 'password1' not in data or 'password2' not in data:
            return Response(data={'error': 'password1 and password2 are required'}, status=status.HTTP_400_BAD_REQUEST)
        if data['password1'] != data['password2']:
            return Response(data={'error': 'Password1 and password2 must be equal'}, status=status.HTTP_400_BAD_REQUEST)
        forgot_key.user.set_password(data['password1'])
        forgot_key.delete()
        return Response(status=status.HTTP_200_OK)
