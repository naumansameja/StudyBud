from rest_framework import serializers
from base.models import Room


class Roomserializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'
