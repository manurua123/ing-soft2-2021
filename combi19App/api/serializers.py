from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import Supplies, Driver, Bus, Place, Route, Profile


class SuppliesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplies
        fields = '__all__'


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = '__all__'


class BusListSerializer(serializers.ModelSerializer):
    driver = serializers.SlugRelatedField(slug_field="fullName", queryset=Driver.objects.all())
    driver_id = serializers.CharField(source='driver.id')

    class Meta:
        model = Bus
        fields = '__all__'


class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = ['id', 'identification']


class PlaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    place = serializers.SerializerMethodField()

    @staticmethod
    def get_place(obj):
        return '{} - {}'.format(obj.town, obj.province)

    class Meta:
        model = Place
        fields = ['id', 'place']


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class RouteListSerializer(serializers.ModelSerializer):
    bus = serializers.SlugRelatedField(slug_field="identification", queryset=Bus.objects.all())
    origin_id = serializers.CharField(source='origin.id')
    destination_id = serializers.CharField(source='destination.id')
    bus_id = serializers.CharField(source='bus.id')
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    @staticmethod
    def get_origin(obj):
        return '{} - {}'.format(obj.origin.town, obj.origin.province)

    @staticmethod
    def get_destination(obj):
        return '{} - {}'.format(obj.destination.town, obj.destination.province)

    class Meta:
        model = Route
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = '__all__'


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']
