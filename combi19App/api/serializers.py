from rest_framework import serializers

from .models import Supplies, Driver, Bus , Place


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
        fields = ('identification', 'model', 'licencePlate', 'seatNumbers', 'driver', 'type')

class PlaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Place
        fields = ('town', 'province')