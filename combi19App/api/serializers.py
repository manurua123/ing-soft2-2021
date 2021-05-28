from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import Supplies, Driver, Bus, Place, Route, Profile, Ticket, Travel, Comment


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
        fields = '__all__'


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
    duration = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    total_minute = serializers.SerializerMethodField()

    @staticmethod
    def get_duration(obj):
        return '{}'.format(obj.duration.strftime("%H:%M"))

    @staticmethod
    def get_total_minute(obj):
        return int('{}'.format(obj.duration.hour * 60 + obj.duration.minute))

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


class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = '__all__'


class TravelListSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(slug_field="id", queryset=Route.objects.all())
    origin = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    departure_date = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    arrival_date = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()

    @staticmethod
    def get_departure_date(obj):
        return '{}'.format(obj.departure_date.date())

    @staticmethod
    def get_departure_time(obj):
        return '{}'.format(obj.departure_date.strftime("%H:%M"))

    @staticmethod
    def get_arrival_date(obj):
        return '{}'.format(obj.arrival_date.date())

    @staticmethod
    def get_arrival_time(obj):
        return '{}'.format(obj.arrival_date.strftime("%H:%M"))

    @staticmethod
    def get_origin(obj):
        return '{} - {}'.format(obj.route.origin.town, obj.route.origin.province)

    @staticmethod
    def get_destination(obj):
        return '{} - {}'.format(obj.route.destination.town, obj.route.destination.province)

    class Meta:
        model = Travel
        fields = ['origin', 'destination', 'route', 'id', 'price', 'departure_date', 'departure_time',
                  'arrival_date', 'arrival_time', 'available_seats']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    @staticmethod
    def get_date(obj):
        return '{}'.format(obj.date.strftime("%d-%m-%Y %H:%M"))

    class Meta:
        model = Comment
        fields = '__all__'
