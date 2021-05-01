from rest_framework import serializers

from .models import Supplies, Driver, Bus, Place, Route


class SuppliesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplies
        fields = "__all__"


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = "__all__"


class BusListSerializer(serializers.ModelSerializer):
    driver = serializers.SlugRelatedField(slug_field="fullName", queryset=Driver.objects.all())

    class Meta:
        model = Bus
        fields = "__all__"

class BusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bus
        fields = "__all__"




class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'

class RouteListSerializer(serializers.ModelSerializer):
    bus = serializers.SlugRelatedField(slug_field="identification", queryset=Bus.objects.all())
    origin = serializers.SlugRelatedField(slug_field="town", queryset=Place.objects.all())
    destiny = serializers.SlugRelatedField(slug_field="town", queryset=Place.objects.all())

    class Meta:
        model = Route
        fields = '__all__'