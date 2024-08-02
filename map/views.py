from django.http import HttpRequest
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from map.models import *
from map import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.settings import CUSTOM_ACCESS_TOKEN_NAME, PURCHASEABLEITEMS
from map.serializers import PropertyViewSerializer, PropertyCreateSerializer
from my_methods.auth import check_login
from authentication.models import History, News


class AllCityApiView(APIView):

    @swagger_auto_schema(
        operation_description="دریافت لیستی از استان ها و شهر ها.",
        responses={
            200: openapi.Response(
                description="لیستی از استان ها و شهر ها",
                examples={
                    "application/json": [
                        {
                            "name": "اصفهان",
                            "is_active": True,
                            "cities": [
                                {
                                    "id": 2,
                                    "name": "اصفهان",
                                    "size": 5,
                                    "unit_price": 5,
                                    "daily_profit": 5,
                                    "is_active": True,
                                    "mayor": None
                                },
                                {
                                    "id": 1,
                                    "name": "نجف آباد",
                                    "size": 11,
                                    "unit_price": 1.14,
                                    "daily_profit": 1.23,
                                    "is_active": True,
                                    "mayor": {
                                        "full_name": "میتی عبوسی",
                                        "username": "mehdi_abbasi"
                                    }
                                }
                            ]
                        },
                        {
                            "name": "خوزستان",
                            "is_active": True,
                            "cities": []
                        }
                    ]
                }
            ),
            404: "استانی پیدا نشد"

        },
    )
    def get(self, request: HttpRequest):
        state = State.objects.filter(is_active=True)
        if state:
            serializer = serializers.StateViewSerializer(state, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CityApiView(APIView):
    @swagger_auto_schema(
        operation_description="دادن آیدی شهر در یو ار ال و دریافت پراپرتی ها و ریلشن های اون شهر .",
        responses={
            200: openapi.Response(
                description="پراپرتی ها و ریلشن ها",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "نجف آباد",
                        "size": 1,
                        "unit_price": 0.01,
                        "daily_profit": 0.01,
                        "is_active": True,
                        "mayor": None,
                        "properties": [
                            {
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
                                "price": "1.12",
                                "position": [
                                    "2",
                                    "3"
                                ],
                                "rotate": 2,
                                "scale": [
                                    "1"
                                ],
                                "type": "c",
                                "object": {
                                    "url": "/templates/objects/card2_copy.jpg",
                                    "price": 0.01
                                },
                                "property_items": [
                                    {
                                        "user": {
                                            "username": "mahdi_abbasi",
                                            "full_name": "mahdi abbasi"
                                        },
                                        "item": {
                                            "title": "میز طلای",
                                            "object_url": "/templates/items/card3.jpg",
                                            "object_name": "میز طلای",
                                            "object_material": "i do no",
                                            "thumbnail": "/templates/items/image/shahrdar.jpg",
                                            "price": 0.03,
                                            "collocation": "gold: 1.90",
                                            "type": "میز",
                                            "profit": 0.05,
                                            "created_at": "2024-06-23T08:47:16.465043Z",
                                            "updated_at": "2024-06-23T08:47:28.717290Z"
                                        },
                                        "position": [
                                            "5",
                                            "6"
                                        ],
                                        "price": 0.05
                                    }
                                ]
                            },
                            {
                                "id": 1,
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
                                "price": "1.01",
                                "position": [
                                    "2",
                                    "5"
                                ],
                                "rotate": 1,
                                "scale": [
                                    "65"
                                ],
                                "type": "5",
                                "object": {
                                    "url": "/templates/objects/card2_copy.jpg",
                                    "price": 0.01
                                },
                                "property_items": [
                                    {
                                        "user": {
                                            "username": "mahdi_abbasi",
                                            "full_name": "mahdi abbasi"
                                        },
                                        "item": {
                                            "title": "شروع دوره های تابستانی",
                                            "object_url": "/templates/items/shahrdar_lHt59qg.jpg",
                                            "object_name": "svg",
                                            "object_material": "vs",
                                            "thumbnail": "/templates/items/image/card3.jpg",
                                            "price": 0.01,
                                            "collocation": "gold: 1.90",
                                            "type": "v",
                                            "profit": -0.01,
                                            "created_at": "2024-06-23T10:24:50.192876Z",
                                            "updated_at": "2024-06-23T10:24:50.192876Z"
                                        },
                                        "position": [
                                            "2",
                                            "8"
                                        ],
                                        "price": 0.01
                                    },
                                    {
                                        "user": {
                                            "username": "mahdi_abbasi",
                                            "full_name": "mahdi abbasi"
                                        },
                                        "item": {
                                            "title": "صندلی طلای",
                                            "object_url": "/templates/items/card3_LG1X7P4.jpg",
                                            "object_name": "صندلی طلای",
                                            "object_material": "س",
                                            "thumbnail": "/templates/items/image/card3_fnJwL3q.jpg",
                                            "price": 0.01,
                                            "collocation": "gold: 1.90",
                                            "type": "س",
                                            "profit": 0.01,
                                            "created_at": "2024-06-23T10:30:01.799909Z",
                                            "updated_at": "2024-06-23T10:30:01.799909Z"
                                        },
                                        "position": [
                                            "2",
                                            "9"
                                        ],
                                        "price": 0.01
                                    }
                                ]
                            }
                        ]
                    }
                }
            ),
            404: "شهر پیدا نشد"

        },
    )
    def get(self, request: HttpRequest, city_id: int):
        city = City.objects.filter(id=city_id).first()
        if city:
            properties = Property.objects.filter(city_id=city)
            data = serializers.city_to_dict(city)
            serializer = serializers.PropertyViewSerializer(properties, many=True)
            data["properties"] = serializer.data
            return Response(data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PropertyApiView(APIView):
    @swagger_auto_schema(
        operation_description="پاک کردن پراپرتی توسط یوزری که رولش superuser باشه .",
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
            204: "با موفقیت پاک شد . ",
            404: "پراپرتی پیدا نشد",
            400: "احراز هویت نشده اید یا ادمین نیستید"
        },
    )
    def delete(self, request: HttpRequest, property_id: int):
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
        check_property = Property.objects.filter(id=property_id).first()
        if check_property:
            check_property.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class CreatPropertyApiView(APIView):
    @swagger_auto_schema(
        operation_description="ثبت پراپرتی.",
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
            400: openapi.Response(description="مشکلی در احراز هویت و یا سوپر یوزر نبودن و یا اشتباه بودن اطلاعات .",
                                  examples={"application/json": "Invalid token"}),
            201: openapi.Response(description="ثبت موفق پراپرتی به همراه اطلاعات ثبت شده.")
        },
    )
    def post(self, request):
        user = check_login(request)
        if user[0]:
            user = user[1]
        else:
            return Response(user[1], status=status.HTTP_400_BAD_REQUEST)

        if user.role != "superuser":
            return Response("Invalid token", status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        serializer = PropertyCreateSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.save()
            serializer = PropertyViewSerializer(data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class BuyPropertyApiView(APIView):
    @swagger_auto_schema(
        operation_description="خرید پراپرتی.",
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
            400: openapi.Response(description="مشکلی در احراز هویت و یا سوپر یوزر نبودن و یا اشتباه بودن اطلاعات .",
                                  examples={"application/json": "Invalid token"}),
            201: openapi.Response(description="خرید موفق پراپرتی ."),
            402: openapi.Response(description="موجودی ناکافی .",
                                  examples={"application/json": "Insufficient inventory"}),
            403: openapi.Response(description="غیر قابل خرید .",
                                  examples={"application/json": "Not available for purchase"}),
            404: openapi.Response(
                description="زمین پیدا نشد یا آیدی اشتباه بوده یا تایپش جاده ای چیزیه که غیر قابل مالک داشتن تایپش ."),
        },
    )
    def post(self, request: HttpRequest, property_id: int):
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
        property = Property.objects.filter(id=property_id).first()
        if property and property.type in PURCHASEABLEITEMS:
            if not property.user_id:
                if user.diamond >= property.price:
                    user_diamond = user.diamond
                    user.diamond -= property.price
                    user.save()
                    description = f'کاربر با پرداخت {property.price} دایموند زمین را خرید و این دایموند از دایموند هاش کم شد و دایموند هاش از {user_diamond} به {user.diamond} تغییر یافت و مالک زمین شد .'
                    History.objects.create(
                        user=user,
                        title=f'خرید زمین با آیدی{property.id}',
                        description=description,
                        location='Property',
                        type='buy'
                    )
                    News.objects.create(
                        text=description,
                    )
                    property.user_id = user
                    property.save()
                    return Response(status=status.HTTP_201_CREATED)
                else:
                    return Response("Insufficient inventory", status=status.HTTP_402_PAYMENT_REQUIRED)
            else:
                return Response("Not available for purchase", status=status.HTTP_403_FORBIDDEN)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
