from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from authentication.models import History, News
from my_methods.auth import check_login
from .serializers import ProfileChangeSerializer, HistorySerializer, NewsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME


class ProfileAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ویرایش اطلاعات کاربر .",
        manual_parameters=[
            openapi.Parameter(
                CUSTOM_ACCESS_TOKEN_NAME,
                openapi.IN_HEADER,
                description="توکن احراز هویت کاربر",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='نام کاربری',
                                           ),
                'full_name': openapi.Schema(type=openapi.TYPE_STRING, description='نام کامل',
                                            ),
                'telegram_id': openapi.Schema(type=openapi.TYPE_STRING, description='آیدی تلگرام',
                                              ),
                'instagram_id': openapi.Schema(type=openapi.TYPE_STRING, description='آیدی اینستاگرام',
                                               ),
                'wallet_address': openapi.Schema(type=openapi.TYPE_STRING, description='آدرس ولت',
                                                 ),
                'cover_url': openapi.Schema(type=openapi.TYPE_FILE, description='کاور'),
                'avatar_url': openapi.Schema(type=openapi.TYPE_FILE, description='آواتار'),
            }
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و یا ویرایش اطلاعات",
                examples={
                    "application/json": {
                        "cover_url": [
                            "The submitted data was not a file. Check the encoding type on the form."
                        ]
                    }
                }
            ),
            200: openapi.Response(
                description="ثبت موفق اطلاعات کاربر و برگرداندن اطلاعات کاربر",
                examples={
                    "application/json": {
                        "username": "mahdi_abbasi",
                        "full_name": "ali abbasi",
                        "telegram_id": None,
                        "instagram_id": None,
                        "wallet_address": None,
                        "cover_url": "https://iranverse.storage.c2.liara.space/iranverse/covers/1384060.png",
                        "avatar_url": None
                    }

                }
            )
        },
    )
    def put(self, request):
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
        serializer = ProfileChangeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if serializer.save():
                return Response(serializer.data)


class GetHistoryAPIView(APIView):
    @swagger_auto_schema(
        operation_description="گرفتن هیستوری های کاربر .",
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
                description="مشکلی در احراز هویت",
                examples={
                    "application/json": 'Access Token Required'
                }
            ),
            200: openapi.Response(
                description="برگرداندن هیستوری کاربر",
                examples={
                    "application/json": [
                        {
                            "title": "خرید زمین با آیدی1",
                            "description": "کاربر با پرداخت 8000000 پوینت زمین را خرید و این پوینت از پوینت هاش کم شد و پوینت هاش از 9000000 به 1000000 تغییر یافت و مالک زمین شد .",
                            "location": "Property",
                            "type": "buy",
                            "created_at": "2024-07-12T18:06:27"
                        }
                    ]

                }
            )
        },
    )
    def get(self, request):
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
        history = History.objects.filter(user_id=user.id)
        if history:
            serializer = HistorySerializer(history, many=True)
            data = serializer.data
            i = 0
            while i < len(data):
                data[i]['created_at'] = data[i]['created_at'][:19]
                i += 1
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetNewsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="گرفتن 10 تا اطلاعیه آخر .",
        responses={
            404: openapi.Response(
                description="اطلاعیه ای نیست",
                examples={
                    "application/json": 'Access Token Required'
                }
            ),
            200: openapi.Response(
                description="برگرداندن اطلاعیه ها",
                examples={
                    "application/json": [
                        {
                            "text": "کاربر با پرداخت 8000000 دایموند زمین را خرید و این دایموند از دایموند هاش کم شد و دایموند هاش از 8000000 به 0 تغییر یافت و مالک زمین شد ."
                        }
                    ]

                }
            )
        },
    )
    def get(self, request):
        news = News.objects.all().order_by('-created_at')
        if news:
            if len(news) > 10:
                serializer = NewsSerializer(news[:10], many=True)
            else:
                serializer = NewsSerializer(news, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
