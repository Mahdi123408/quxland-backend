from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from my_methods.auth import check_login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME
from files.serializers import FileCreateSerializer, FileViewSerializer
from files.models import *


class UploadAPIView(APIView):
    @swagger_auto_schema(
        operation_description="ایجاد فایل.",
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
                'file': openapi.Schema(type=openapi.TYPE_FILE, description='فایل',
                                       ),
                'alt': openapi.Schema(type=openapi.TYPE_STRING, description='توضیحات',
                                      ),
            },
            required=['file', 'alt']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و یا ایجاد فایل",
                examples={
                    "application/json": {
                        "file": [
                            "No file was submitted."
                        ],
                        "alt": [
                            "This field is required."
                        ]
                    }
                }
            ),
            201: openapi.Response(
                description="ایحاد موفق فایل و برگرداندن فایل",
                examples={
                    "application/json": {
                        "file": "https://iranverse.storage.c2.liara.space/iranverse/files/1384060.png",
                        "alt": "رب"
                    }
                }
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
        if user.role != "superuser":
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        data = request.data
        serializer = FileCreateSerializer(data=data, user=user)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetFilesAPIView(APIView):
    @swagger_auto_schema(
        operation_description="گرفتن همه فایل ها.",
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
                    "application/json": "Invalid token"
                }
            ),
            200: openapi.Response(
                description="برگرداندن فایل ها",
                examples={
                    "application/json": [
                        {
                            "id": 30,
                            "file": "https://iranverse.storage.c2.liara.space/iranverse/files/5_1.jpeg",
                            "alt": "test",
                            "user": {
                                "id": 1,
                                "username": "mahdi_abbasi",
                                "full_name": "ali abbasi",
                                "diamond": 1000000,
                                "rating": 0,
                                "level": 0,
                                "avatar_url": None,
                                "cover_url": "https://iranverse.storage.c2.liara.space/iranverse/covers/1384060.png",
                                "telegram_id": None,
                                "instagram_id": None,
                                "points": 6,
                                "created_at": "2024-07-06 13:28:01"
                            },
                            "is_public": False,
                            "is_active": True
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
        if user.role != "superuser":
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)
        files = Files.objects.all()
        if files:
            serializer = FileViewSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
