from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from my_methods.auth import check_login
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME
from weblog.models import *
from weblog.serializers import *


class WeblogReadAndCreateAPIView(APIView):
    @swagger_auto_schema(
        operation_description="دسته بندی مقالات به همراه مقالات .",
        responses={
            200: openapi.Response(
                description="دسته بندی ها و مقالاتشون",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "name": "راهنمایی",
                            "article": [
                                {
                                    "id": 1,
                                    "title": "شروع دوره های تابستانی",
                                    "content": "نعلمهلبعنعمعبنعللعلنعلبنعبن",
                                    "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/4.png",
                                    "short_description": "خمهبعن ن    لهنل علعنل ننعل نلعنن ل لعنل نلعل لنعل  لنلن  لن ن لنع ن لنت عنا",
                                    "created_at": "2024-07-14T22:20:14.140032+03:30",
                                    "updated_at": "2024-07-14T22:20:14.140032+03:30",
                                    "category_id": {
                                        "id": 1,
                                        "name": "راهنمایی"
                                    },
                                    "published_at": "2024-07-14T22:18:53+03:30",
                                    "is_active": True
                                }
                            ]
                        },
                        {
                            "id": 2,
                            "name": "درباره ما",
                            "article": [
                                {
                                    "id": 4,
                                    "title": "gyh",
                                    "content": "ئابدلذزبط",
                                    "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/8.png",
                                    "short_description": "خگحههاغتل",
                                    "created_at": "2024-07-14T22:21:34.695506+03:30",
                                    "updated_at": "2024-07-14T22:32:15.773925+03:30",
                                    "category_id": {
                                        "id": 2,
                                        "name": "درباره ما"
                                    },
                                    "published_at": "2024-07-14T22:32:14+03:30",
                                    "is_active": True
                                }
                            ]
                        }
                    ]
                }
            ),
            404: "دستبندی مقاله ای یافت نشد"

        },
    )
    def get(self, request):
        categorys = Category.objects.all()
        if categorys:
            serializer = CategoryViewSerializer(categorys, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="ایجاد مقاله .",
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
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='عنوان',
                                        ),
                'thumbnail': openapi.Schema(type=openapi.TYPE_FILE, description='عکس',
                                            ),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='محتوا',
                                          ),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='دسته بندی',
                                           ),
                'short_description': openapi.Schema(type=openapi.TYPE_STRING, description='توضیحات کوتاه',
                                                    ),
                'published_at': openapi.Schema(type=openapi.TYPE_STRING, description='نمایش بده بعد از',
                                               default='2024-07-15 22:32:14'),
            },
            required=['title', 'thumbnail', 'content', 'category', 'short_description', 'published_at']
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و یا ایجاد مقاله",
                examples={
                    "application/json": {
                        "title": [
                            "This field is required."
                        ],
                        "thumbnail": [
                            "No file was submitted."
                        ],
                        "content": [
                            "This field is required."
                        ],
                        "category": [
                            "This field is required."
                        ],
                        "short_description": [
                            "This field is required."
                        ],
                        "published_at": [
                            "This field is required."
                        ]
                    }
                }
            ),
            201: openapi.Response(
                description="ایحاد موفق مقاله و برگرداندن مقاله",
                examples={
                    "application/json": {
                        "title": "test from api",
                        "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/1384060.png",
                        "content": "thdgrfs",
                        "category": 1,
                        "short_description": "ljiikhjgcf",
                        "published_at": "2024-07-15T22:32:14"
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
        serializer = CreateArticleSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            data = serializer.data
            data['published_at'] = data['published_at'][:19]
            return Response(data, status=status.HTTP_201_CREATED)


class EditAndDeleteArticleAPIView(APIView):
    @swagger_auto_schema(
        operation_description="حذف مقاله .",
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
            204: openapi.Response(
                description="حذف موفق",
            ),
            404: openapi.Response(
                description="پیدا نشدن آیدی",
            )
        },
    )
    def delete(self, request, article_id: int):
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
        article = Article.objects.filter(id=article_id).first()
        if article:
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="ویرایش مقاله .",
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
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='عنوان',
                                        ),
                'thumbnail': openapi.Schema(type=openapi.TYPE_FILE, description='عکس',
                                            ),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='محتوا',
                                          ),
                'category': openapi.Schema(type=openapi.TYPE_INTEGER, description='دسته بندی',
                                           ),
                'short_description': openapi.Schema(type=openapi.TYPE_STRING, description='توضیحات کوتاه',
                                                    ),
                'published_at': openapi.Schema(type=openapi.TYPE_STRING, description='نمایش بده بعد از',
                                               default='2024-07-15 22:32:14'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='فعال است',
                                            default=False),
            },
        ),
        responses={
            400: openapi.Response(
                description="مشکلی در احراز هویت و یا ویرایش مقاله",
                examples={
                    "thumbnail": [
                        "The submitted data was not a file. Check the encoding type on the form."
                    ]
                }
            ),
            200: openapi.Response(
                description="ویرایش موفق مقاله و برگرداندن مقاله",
                examples={
                    "application/json": {
                        "title": "test from api",
                        "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/51w1.jpeg",
                        "content": "ئابدلذزبط",
                        "category": 2,
                        "short_description": "خگحههاغتل",
                        "published_at": "2024-07-15T00:40:53",
                        "is_active": True
                    }
                }
            )
        },
    )
    def put(self, request, article_id: int):
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
        article = Article.objects.filter(id=article_id).first()
        if article:
            data = request.data
            serializer = ArticleChangeSerializer(article, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                if serializer.save():
                    data = serializer.data
                    data['published_at'] = data['published_at'][:19]
                    return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="گرفتن مقاله با آیدی .",
        responses={
            200: openapi.Response(
                description="مقاله",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "شروع دوره های تابستانی",
                        "content": "نعلمهلبعنعمعبنعللعلنعلبنعبن",
                        "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/4.png",
                        "short_description": "خمهبعن ن    لهنل علعنل ننعل نلعنن ل لعنل نلعل لنعل  لنلن  لن ن لنع ن لنت عنا",
                        "created_at": "2024-07-14T22:20:14.140032+03:30",
                        "updated_at": "2024-07-17T13:31:52.375678+03:30",
                        "category_id": {
                            "id": 1,
                            "name": "راهنمایی"
                        },
                        "published_at": "2024-07-17T13:31:36+03:30",
                        "is_active": True,
                        "articles": [
                            {
                                "id": 2,
                                "title": "صندلی طلای",
                                "content": "ئائئبابابد ددبد  دبفذدب ب بد بد د بدفدد د ب دبب بف بف ذب ب",
                                "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/7_oKJoE1M.png",
                                "short_description": "فبابایلیقدلقلاف",
                                "created_at": "2024-07-14T22:20:49.716564+03:30",
                                "updated_at": "2024-07-14T22:20:49.716564+03:30",
                                "category_id": {
                                    "id": 1,
                                    "name": "راهنمایی"
                                },
                                "published_at": "2024-07-15T22:20:44+03:30",
                                "is_active": True
                            },
                            {
                                "id": 3,
                                "title": "tbbd",
                                "content": "ثیاب",
                                "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/6.png",
                                "short_description": "بی",
                                "created_at": "2024-07-14T22:21:17.345701+03:30",
                                "updated_at": "2024-07-14T22:31:40.842292+03:30",
                                "category_id": {
                                    "id": 2,
                                    "name": "درباره ما"
                                },
                                "published_at": "2024-07-15T22:21:14+03:30",
                                "is_active": True
                            },
                            {
                                "id": 4,
                                "title": "test from api",
                                "content": "ئابدلذزبط",
                                "thumbnail": "https://iranverse.storage.c2.liara.space/iranverse/articles/51w1.jpeg",
                                "short_description": "خگحههاغتل",
                                "created_at": "2024-07-14T22:21:34.695506+03:30",
                                "updated_at": "2024-07-15T00:46:32.474071+03:30",
                                "category_id": {
                                    "id": 2,
                                    "name": "درباره ما"
                                },
                                "published_at": "2024-07-15T00:40:53+03:30",
                                "is_active": True
                            }
                        ]
                    }
                }
            ),
            404: "مقاله ای یافت نشد"

        },
    )
    def get(self, request, article_id: int):
        now = timezone.now()
        article = Article.objects.filter(id=article_id, published_at__lte=now, is_active=True).first()
        if article:
            articles = Article.objects.exclude(id=1).filter(published_at__lte=now, is_active=True).exclude(
                id=article.id).order_by('-created_at')
            serializer = ArticleViewSerializer(article)
            data = serializer.data
            if articles:
                articles_data = ArticleViewSerializer(articles, many=True).data
                if len(articles_data) <= 3:
                    data['articles'] = articles_data
                else:
                    data['articles'] = articles_data[:3]
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
