from django.http import HttpRequest
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from my_methods.auth import check_login
from click.serializers import UserAndClickSerializer
from click.models import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME


class UserDataAPIView(APIView):
    @swagger_auto_schema(
        operation_description="اطلاعات یوزر برای ایر دراپ کلیکی . ",
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
                    description="اطلاعات یوزر برای ایر دراپ کلیکی . ",
                    examples={
                        "application/json": {
                            "username": "mahdi_abbasi",
                            "email": "abasimahdi243@gmail.com",
                            "full_name": "mahdi abbasi",
                            "point": 0,
                            "profile": None,
                            "ref": [],
                            "level": 1
                        }
                    }
                )
        },
    )
    def get(self, request: HttpRequest):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        ac_user = AccountUser.objects.filter(user=user).first()
        if not ac_user:
            ac_user = AccountUser(user=user, time_last_claim=datetime.now())
            ac_user.save()
        else:
            ac_user = user.click_account
        serializer = UserAndClickSerializer(user)
        return Response(serializer.data)


class AddClickAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ثبت پوینت برای ایر دراپ کلیکی . ",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'count': openapi.Schema(type=openapi.TYPE_INTEGER, description='تعداد پوینت'),
            },
            required=['count']
        ),
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
                    description="ثبت موفق پوینت . "
                ),
            204:
                openapi.Response(
                    description="ناموفق . "
                )
        },
    )
    def post(self, request):
        user = check_login(request)
        if user[0]:
            user = user[1]
        elif user[1] == 'Invalid token':
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Token expired':
            return Response("Token expired", status=status.HTTP_400_BAD_REQUEST)
        elif user[1] == 'Access Token Required':
            return Response("Access Token Required", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        ac_user = AccountUser.objects.filter(user=user).first()
        if not ac_user:
            ac_user = AccountUser(user=user, time_last_claim=datetime.now())
            ac_user.save()
        else:
            ac_user = user.click_account
        if 'count' in request.data:
            count = request.data['count']
            if ac_user.add_claim(count=count):
                return Response()
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
