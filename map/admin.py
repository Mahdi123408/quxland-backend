from django.contrib import admin
from map import models


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'size', 'unit_price', 'daily_profit', 'is_active', 'mayor')
    list_editable = ['is_active', ]
    list_filter = ('state', 'is_active')


@admin.register(models.State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'cities')
    list_editable = ['is_active', ]

    def cities(self, obj):
        x = ''
        cities = obj.cities.filter(is_active=True)
        if cities:
            for city in cities:
                x += city.name + ' , '
        return x


@admin.register(models.Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_id', 'price', 'position', 'rotate', 'scale', 'type', 'object_id', 'city_id']


@admin.register(models.PropertyItem)
class PropertyItemAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'item', 'position', 'price', 'is_active']


@admin.register(models.Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ['object_url', 'price', 'created_at', 'updated_at']


@admin.register(models.ObjectItem)
class ObjectItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'object', 'created_at', 'updated_at']


@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'object_url', 'object_name', 'object_material', 'thumbnail', 'price', 'collocation',
                    'type', 'profit', 'created_at', 'updated_at', 'is_active']


@admin.register(models.ItemCollocation)
class ItemCollocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'leverage', 'created_at', 'updated_at', 'is_active']
