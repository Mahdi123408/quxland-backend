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
from setting.models import Rule
from setting.serializers import RuleSerializer


class RuleAPIView(APIView):
    @swagger_auto_schema(
        operation_description="قوانین .",
        responses={
            200: openapi.Response(
                description="برگشتن قوانین",
                examples={
                    "application/json": {
                        "id": 1,
                        "title": "tt6",
                        "short_desc": "refzh",
                        "content": "![](https://iranverse.storage.c2.liara.space/iranverse/20240803114145584200.png)![](https://iranverse.storage.c2.liara.space/iranverse/20240803114213921744.png)",
                        "is_active": True,
                        "created_at": "2024-08-03T11:42:35",
                        "updated_at": "2024-08-03T11:43:34"
                    }
                }
            ),
            404: "قانونی یافت نشد"
        },
    )
    def get(self, request):
        rule = Rule.objects.filter(is_active=True).first()
        if not rule:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = RuleSerializer(rule)
        data = serializer.data
        data['created_at'] = data['created_at'][:19]
        data['updated_at'] = data['updated_at'][:19]
        return Response(data)
