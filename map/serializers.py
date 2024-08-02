from rest_framework import serializers
from map.models import *


def city_to_dict(city):
    if not city.mayor:
        return {
            'id': city.id,
            'name': city.name,
            'size': city.size,
            'unit_price': city.unit_price,
            'daily_profit': city.daily_profit,
            'is_active': city.is_active,
            'mayor': city.mayor
        }
    else:
        mayor = city.mayor
        try:
            mayor = {
                'full_name': mayor.full_name,
                'username': mayor.username
            }
        except AttributeError:
            mayor = None
        return {
            'id': city.id,
            'name': city.name,
            'size': city.size,
            'unit_price': city.unit_price,
            'daily_profit': city.daily_profit,
            'is_active': city.is_active,
            'mayor': mayor
        }


class StateViewSerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = ['name', 'is_active', 'cities']

    def get_cities(self, obj):
        cities = obj.cities.filter(is_active=True)
        l = []
        if cities:
            for city in cities:
                l.append(city_to_dict(city))
        return l


class PropertyViewSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    object = serializers.SerializerMethodField()
    property_items = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = ['id', 'user', 'price', 'position', 'rotate', 'scale', 'type', 'object', 'property_items']

    def get_user(self, obj):
        if obj.user_id:
            return obj.user_id.to_dict()
        else:
            return None

    def get_object(self, obj):
        if obj.object_id:
            return {
                'url': obj.object_id.object.object_url.url,
                'price': obj.object_id.object.price,
            }
        else:
            return None

    def get_property_items(self, obj):
        if obj.items:
            l2 = []
            items = obj.items.filter(is_active=True)
            for item in items:
                if item.user:
                    user = {
                        'username': item.user.username,
                        'full_name': item.user.full_name,
                    }
                else:
                    user = None

                if item.item.is_active:
                    p_items = item.item
                else:
                    p_items = None
                if p_items:
                    p_item = {
                        'title': p_items.title,
                        'object_url': p_items.object_url.url,
                        'object_name': p_items.object_name,
                        'object_material': p_items.object_material,
                        'thumbnail': p_items.thumbnail.url,
                        'price': p_items.price,
                        'collocation': f'{p_items.collocation.name}: {p_items.collocation.leverage}',
                        'type': p_items.type,
                        'profit': p_items.profit,
                        'created_at': p_items.created_at,
                        'updated_at': p_items.updated_at,
                    }
                else:
                    p_item = None
                l2.append(
                    {
                        'user': user,
                        'item': p_item,
                        'position': item.position,
                        'price': item.price
                    }
                )
            return l2
        else:
            return None


class PropertyCreateSerializer(serializers.ModelSerializer):
    id_city = serializers.CharField(write_only=True)
    position = serializers.ListField(child=serializers.CharField())
    scale = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Property
        fields = ['position', 'rotate', 'scale', 'type', 'id_city']

    def validate_id_city(self, value):
        check_city = City.objects.filter(id=value).first()
        if not check_city:
            raise serializers.ValidationError("no city found")
        return check_city

    def create(self, validated_data):
        check_city = validated_data.pop('id_city')
        ins_property = Property(**validated_data)
        ins_property.city_id = check_city
        ins_property.save()
        return ins_property
