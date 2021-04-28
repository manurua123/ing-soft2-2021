from rest_framework import serializers

from .models import Supplies, Driver, Bus, Place, Route


class SuppliesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Supplies
        fields = ('description', 'price')


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Driver
        fields = ('fullName', 'firstName', 'lastName', 'email', 'phone')


class BusSerializer(serializers.HyperlinkedModelSerializer):
    driver = serializers.SlugRelatedField(slug_field="fullName", queryset=Driver.objects.all())
    class Meta:
        model = Bus
        fields = ('id','identification', 'model', 'licencePlate', 'seatNumbers', 'driver', 'type')

class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = ('id','town', 'province')

class RouteSerializer(serializers.ModelSerializer ):
    bus = BusSerializer()
    origin = PlaceSerializer()
    destiny = PlaceSerializer()
    class Meta:
        model = Route
        fields = ( 'origin', 'destiny', 'bus', 'duration', 'distance',)