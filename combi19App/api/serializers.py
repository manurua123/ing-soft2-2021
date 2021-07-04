from datetime import datetime
import json
from django.forms.models import model_to_dict

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
    seat_numbers = serializers.CharField(source='bus.seatNumbers')

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


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    @staticmethod
    def get_rol(obj):
        return obj.groups.get().name

    class Meta:
        model = User
        fields = ['username', 'last_name', 'first_name', 'email', 'rol']


class UserSignSerializer(serializers.ModelSerializer):
    rol = serializers.SerializerMethodField()

    @staticmethod
    def get_rol(obj):
        return obj.groups.get().name

    class Meta:
        model = User
        fields = ['username', 'rol', 'id']


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    gold = serializers.SerializerMethodField()
    user_id = serializers.CharField(source='user.id')
    suspension = serializers.SerializerMethodField()

    @staticmethod
    def get_suspension(obj):
        if obj.end_date_suspension is None or obj.end_date_suspension < datetime.now().date():
            return False
        return True

    @staticmethod
    def get_gold(obj):
        return obj.card_holder is not None

    class Meta:
        model = Profile
        fields = '__all__'


class ProfileSignSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    user_id = serializers.CharField(source='user.id')
    gold = serializers.SerializerMethodField()
    rol = serializers.SerializerMethodField()
    suspension = serializers.SerializerMethodField()

    @staticmethod
    def get_gold(obj):
        return obj.card_holder is not None

    @staticmethod
    def get_rol(obj):
        return obj.user.groups.get().name

    @staticmethod
    def get_suspension(obj):
        if obj.end_date_suspension is None or obj.end_date_suspension < datetime.now().date():
            return False
        return True

    class Meta:
        model = Profile
        fields = ['user', 'rol', 'gold', 'user_id', 'suspension']


class TravelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Travel
        fields = '__all__'


class TravelListSerializer(serializers.ModelSerializer):
    route = serializers.SlugRelatedField(slug_field="id", queryset=Route.objects.all())
    origin = serializers.SerializerMethodField()
    type_bus = serializers.CharField(source='route.bus.type')
    bus_id = serializers.CharField(source='route.bus.identification')
    duration = serializers.CharField(source='route.duration')
    destination = serializers.SerializerMethodField()
    departure_date = serializers.SerializerMethodField()
    departure_time = serializers.SerializerMethodField()
    arrival_date = serializers.SerializerMethodField()
    arrival_time = serializers.SerializerMethodField()
    driver_name = serializers.SerializerMethodField()
    can_init_travel = serializers.SerializerMethodField()

    @staticmethod
    def get_driver_name(obj):
        user = User.objects.get(id=obj.driver)
        return '{}, {}'.format(user.last_name, user.first_name)

    @staticmethod
    def get_can_init_travel(obj):
        tickets = Ticket.objects.filter(travel=obj.id)
        if not tickets:
            return False
        else:
            return not tickets.filter(state='Activo')

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
                  'arrival_date', 'arrival_time', 'available_seats', 'duration', 'state', 'type_bus',
                  'bus_id', 'ticket_sold', 'can_init_travel', 'driver_name', 'delete']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class TicketRejectedSerializer(serializers.ModelSerializer):
    travel = TravelListSerializer()
    user = UserSerializer()
    profile = serializers.SerializerMethodField()

    @staticmethod
    def get_profile(obj):
        profile = Profile.objects.get(user=obj.user.pk)
        profile_d = model_to_dict(profile)
        return json.dumps(profile_d, sort_keys=True, default=str, ensure_ascii=True)

    class Meta:
        model = Ticket
        fields = '__all__'


class TicketListSerializer(serializers.ModelSerializer):
    travel = TravelListSerializer()
    user_id = serializers.CharField(source='user.id')

    class Meta:
        model = Ticket
        fields = '__all__'


class CommentListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    user = serializers.SlugRelatedField(slug_field="id", queryset=User.objects.all())
    user_first_name = serializers.CharField(source='user.first_name')
    user_last_name = serializers.CharField(source='user.last_name')

    @staticmethod
    def get_date(obj):
        return '{}'.format(obj.date.strftime("%d/%m/%Y"))

    class Meta:
        model = Comment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()

    @staticmethod
    def get_date(obj):
        return '{}'.format(obj.date.strftime("%d/%m/%Y"))

    class Meta:
        model = Comment
        fields = '__all__'
