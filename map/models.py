from django.db import models
from authentication.models import CustomUser
from django.contrib.postgres.fields import ArrayField


class State(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'States'
        verbose_name = 'State'
        ordering = ['name']


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    size = models.IntegerField()
    unit_price = models.IntegerField()
    daily_profit = models.IntegerField()
    is_active = models.BooleanField(default=True)
    mayor = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cities')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Cities'
        verbose_name = 'City'
        ordering = ['name']

    def to_dict(self):
        return {
            'name': self.name,
            'size': self.size,
            'unit_price': self.unit_price,
            'daily_profit': self.daily_profit,
            'is_active': self.is_active,
            'mayor': self.mayor.name,
        }

    def save(self, *args, **kwargs):
        super(City, self).save(*args, **kwargs)
        properties = Property.objects.filter(city_id_id=self.id)
        if properties:
            for prop in properties:
                if len(prop.scale) == 2:
                    prop.price = self.unit_price * (prop.scale[0] * prop.scale[1])
                else:
                    prop.price = 1111111111111111
                prop.save()


class Object(models.Model):
    object_url = models.FileField(upload_to='objects')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.object_url.name

    class Meta:
        verbose_name_plural = 'Objects'
        verbose_name = 'Object'


class ObjectItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='object_items')
    object = models.ForeignKey(Object, on_delete=models.CASCADE, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}: {self.object}'

    class Meta:
        verbose_name_plural = 'ObjectItems'
        verbose_name = 'ObjectItem'


class Property(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='user')
    price = models.IntegerField()
    position = ArrayField(models.CharField(max_length=100), default=list)
    rotate = models.IntegerField(default=0)
    scale = ArrayField(models.IntegerField(), default=list)
    type = models.CharField(max_length=100)
    object_id = models.ForeignKey(ObjectItem, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='properties')
    city_id = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')

    def __str__(self):
        return f'{self.city_id}: {self.type}'

    class Meta:
        verbose_name_plural = 'Properties'
        verbose_name = 'Property'

    def save(self, *args, **kwargs):
        if len(self.scale) == 2:
            self.price = self.city_id.unit_price * (int(self.scale[0]) * int(self.scale[1]))
        else:
            self.price = 1111111111111111
        super(Property, self).save(*args, **kwargs)


class ItemCollocation(models.Model):
    name = models.CharField(max_length=100)
    leverage = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}: {self.leverage}'

    class Meta:
        verbose_name_plural = 'ItemCollocations'
        verbose_name = 'ItemCollocation'


class Item(models.Model):
    title = models.CharField(max_length=100)
    object_url = models.FileField(upload_to='items')
    object_name = models.CharField(max_length=100)
    object_material = models.CharField(max_length=100)
    thumbnail = models.ImageField(upload_to='items/image')
    price = models.DecimalField(max_digits=5, decimal_places=2)
    collocation = models.ForeignKey(ItemCollocation, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    profit = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Items'
        verbose_name = 'Item'


class PropertyItem(models.Model):
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='properties')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='properties')
    position = ArrayField(models.CharField(max_length=100), default=list, null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)  # قیمت لحظه ای که خریداری شده
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user}: {self.item}'

    class Meta:
        verbose_name_plural = 'PropertyItems'
        verbose_name = 'PropertyItem'
