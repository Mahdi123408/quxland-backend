from rest_framework import serializers
from transaction.models import *


class DiamondSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiamondPackage
        fields = '__all__'
