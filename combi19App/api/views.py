from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.core import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User, Group
from datetimerange import DateTimeRange
from datetime import datetime, timedelta
from datetime import timezone
import json
from django.forms.models import model_to_dict
from django.db import transaction

from .serializers import SuppliesSerializer, DriverSerializer, BusSerializer, PlaceListSerializer, RouteSerializer, \
    RouteListSerializer, BusListSerializer, PlaceSerializer, ProfileSerializer, RolSerializer, TravelSerializer, \
    TravelListSerializer, TicketSerializer, CommentSerializer, TicketListSerializer, ProfileSignSerializer, \
    UserSignSerializer, UserSerializer, CommentListSerializer, TicketRejectedSerializer

from .models import Supplies, Driver, Bus, Place, Route, Profile, Ticket, SuppliesDetail, Travel, Comment
from rest_framework.response import Response
from django.db.models import Q


class SuppliesViewSet(viewsets.ModelViewSet):
    queryset = Supplies.objects.filter(delete=False).order_by('description')
    serializer_class = SuppliesSerializer

    # permission_classes = [IsAuthenticated]
    @action(detail=False)
    def all(self, request):
        supplies = Supplies.objects.filter(delete=False).order_by('description')
        serializer = SuppliesSerializer(supplies, many=True)
        return Response(serializer.data)  # status 200

    def create(self, request):
        suppliesData = request.data
        try:
            supplies = Supplies.objects.get(description=suppliesData["description"])
            if supplies.delete:
                supplies.delete = False
                serializer = SuppliesSerializer(supplies, data=suppliesData, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200
            data = {
                'code': 'supplies_exists_error',
                'message': 'El insumo ' + supplies.description + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Supplies.DoesNotExist:
            serializer = SuppliesSerializer(data=suppliesData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        suppliesData = request.data
        supplies = self.get_object()
        try:
            suppliesSearch = Supplies.objects.get(description=suppliesData["description"])
            if str(suppliesSearch.id) != str(pk):
                data = {
                    'code': 'supplies_exists_error',
                    'message': 'El insumo ' + suppliesSearch.description + ' ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            serializer = SuppliesSerializer(supplies, data=suppliesData, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200
        except Supplies.DoesNotExist:
            serializer = SuppliesSerializer(supplies, data=suppliesData, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        supplies = self.get_object()
        supplies.delete = True
        serializer = SuppliesSerializer(supplies, data=supplies.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.filter(delete=False).order_by('fullName')
    serializer_class = DriverSerializer

    @action(detail=False)
    def all(self, request):
        driver = Driver.objects.filter(delete=False).order_by('fullName')
        serializer = DriverSerializer(driver, many=True)
        return Response(serializer.data)  # status 200

    @transaction.atomic
    def create(self, request):
        driverData = request.data
        try:
            # Controla si ya existe el email del chofer a crear
            driver = Driver.objects.get(email=driverData["email"])
            # Si existe informa que ya fue registrado anteriormente
            data = {
                'code': 'driver_exists_error',
                'message': 'El chofer con el email ' + driver.email + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no existe lo agrega como un nuevo chofer
        except Driver.DoesNotExist:
            rol = Group.objects.get(name='DRIVER')
            userNew = User.objects.create_user(username=driverData["email"], email=driverData["email"],
                                               password=driverData["email"], last_name=driverData["lastName"],
                                               first_name=driverData["firstName"])
            rol.user_set.add(userNew)
            profile = Profile.objects.create(user=userNew,
                                             birth_date=driverData["birth_date"], phone=driverData["phone"],
                                             idCards=driverData["idCards"])
            profile.save()
            driverData["fullName"] = driverData["lastName"] + ', ' + driverData["firstName"]
            serializer = DriverSerializer(data=driverData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    @transaction.atomic
    def update(self, request, pk=None):
        driverData = request.data
        try:
            driver = Driver.objects.get(email=driverData["email"])
            if str(driver.id) == str(pk):
                user = User.objects.get(email=driver.email)
                user.last_name = driverData["lastName"]
                user.first_name = driverData["firstName"]
                user.save()
                profile = Profile.objects.get(user_id=user.id)
                profile.birth_date = driverData["birth_date"]
                profile.idCards = driverData["idCards"]
                profile.phone = driverData["phone"]
                profile.save()
                driverData["fullName"] = driverData["lastName"] + ', ' + driverData["firstName"]
                serializer = DriverSerializer(driver, data=driverData, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200

            data = {
                'code': 'driver_update_already_exists',
                'message': 'El correo electr??nico: ' + driver.email + ' ya se encuentra registrado.'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Driver.DoesNotExist:
            data = {
                'code': 'driver_update_not_exists',
                'message': 'No existe el chofer que esta tratando de modificar'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        driver = self.get_object()
        # Controla que el chofer a eliminar no pertenezca a una combi activa
        driverInBus = Bus.objects.filter(driver=kwargs.get('pk'), delete=False)
        # Si pertenece a una Combi activa informa que no puede eliminar
        if driverInBus:
            data = {
                'code': 'driver_exists_in_bus_error',
                'message': 'El chofer ' + driver.__str__() + ' no se puede eliminar porque existe en un veh??culo Activo'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no pertenece a una Combi activa realiza el marcado logico de borrado como un update
        user = User.objects.get(email=driver.email)
        user.is_active = False
        user.save()
        profile = Profile.objects.get(user_id=user.id)
        profile.delete = True
        profile.save()
        driver.delete = True
        serializer = DriverSerializer(driver, data=driver.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.filter(delete=False).order_by('identification')
    serializer_class = BusListSerializer

    @action(detail=False)
    def all(self, request):
        bus = Bus.objects.filter(delete=False).order_by('identification')
        serializer = BusSerializer(bus, many=True)
        return Response(serializer.data)  # status 200

    def create(self, request):
        busData = request.data
        try:
            # Controla si el veh??culo a crear ya existe

            bus = Bus.objects.get(identification=busData['identification'])

            # Si existe el vehiculo pero esta borrado lo reactiva
            if bus.delete and (bus.licencePlate == busData['licencePlate']):
                bus.delete = False
                serializer = BusSerializer(bus, data=busData, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200

            # Si existe pero no esta borrado informa que ya ha sido registrado anteriormente
            data = {
                'code': 'bus_exists_error',
                'message': 'La identificacion ' + bus.__str__() + ' que esta tratando de crear ya ha sido registrada con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Bus.DoesNotExist:
            # Si no existe Busca que el chofer no este ya registrado en un veh??culo
            driverInBus = Bus.objects.filter(driver=busData['driver'], delete=False)
            if driverInBus:
                data = {
                    'code': 'driver_exists_in_bus_error',
                    'message': 'El chofer ' + driverInBus[0].driver.__str__() + ' ya est?? registrado en otro veh??culo'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            # Crea un nuevo veh??culo
            serializer = BusSerializer(data=busData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        busData = request.data
        bus = self.get_object()
        # Controla que el vehiculo a modificar no pertenezca a un viaje activo
        busInTravel = Travel.objects.filter((Q(state='Iniciado') | Q(state='Pendiente')), route__bus=pk,
                                            delete=False, route__delete=False)
        if busInTravel:
            data = {
                'code': 'bus_exists_in_travel_error',
                'message': 'El veh??culo ' + bus.__str__() + ' que esta tratando de modificar se encuentra en un viaje activo'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        try:

            # Controla si la combi modificada ya existe
            busSearch = Bus.objects.get(identification=busData['identification'])
            # Si la encuentra informa que no se puede modificar porque ya existe anteriormente
            if str(busSearch.id) != str(pk):
                data = {
                    'code': 'bus_exists_error',
                    'message': 'El veh??culo ' + str(
                        busSearch) + ' que esta tratando de modificar ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            driverInBus = Bus.objects.filter(driver=busData['driver'], delete=False)

            if driverInBus and str(bus.driver) != str(driverInBus[0].driver):
                data = {
                    'code': 'driver_exists_in_bus_error',
                    'message': 'El chofer ' + driverInBus[0].driver.__str__() + ' ya est?? registrado en otro veh??culo'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

            serializer = BusSerializer(bus, data=busData, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200
        except Bus.DoesNotExist:
            serializer = BusSerializer(bus, data=busData, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        bus = self.get_object()
        # Controla que la Combi a eliminar no pertenezca a una ruta activa
        busInRoute = Route.objects.filter(bus=kwargs.get('pk'), delete=False)
        # Si pertenece a una ruta activa informa que no puede eliminarla
        if busInRoute:
            data = {
                'code': 'bus_exists_in_route_error',
                'message': 'El veh??culo ' + bus.__str__() + ' no se puede eliminar porque existe en una ruta activa'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no pertenece a una ruta activa realiza el marcado logico de borrado como un update
        bus.delete = True
        serializer = BusSerializer(bus, data=bus.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.filter(delete=False).order_by('province', 'town')
    serializer_class = PlaceListSerializer
    pagination_class = PageNumberPagination

    @action(detail=False)
    def all(self, request):
        place = Place.objects.filter(delete=False).order_by('province', 'town')
        serializer = PlaceSerializer(place, many=True)
        return Response(serializer.data)  # status 200

    def create(self, request):
        placeData = request.data
        try:
            # Busca si el lugar a crear ya existe
            place = Place.objects.get(town=placeData["town"], province=placeData["province"])
            # Si existe pero esta borrado lo reactiva
            if place.delete:
                place.delete = False
                serializer = PlaceListSerializer(place, data=place.__dict__, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200
            # Si existe pero no esta borrado informa que ya est?? anteriormente registrado
            data = {
                'code': 'place_exists_error',
                'message': 'El lugar ' + place.__str__() + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no existe lo registra como un nuevo lugar
        except Place.DoesNotExist:
            serializer = PlaceListSerializer(data=placeData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        placeData = request.data
        place = self.get_object()
        serializer = PlaceListSerializer(place, data=placeData, partial=True)
        serializer.is_valid(raise_exception=True)
        # Primero controla si el lugar a modificar no se encuentra en alguna ruta activa
        placeInRoute = Route.objects.filter((Q(origin=pk) | Q(destination=pk)), delete=False)
        # Si el lugar esta en una ruta activa informa que no lo puede modificar
        if placeInRoute:
            data = {
                'code': 'place_exists_in_route_error',
                'message': 'El lugar ' + place.__str__() + ' no se puede modificar porque pertenece a una ruta activa'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no esta en una ruta activa sigue con otro control
        try:
            # Luego controla que la modificacion no sea un lugar ya registrado, ojo no filtra los borrados
            placeSearch = Place.objects.get(town=placeData["town"], province=placeData["province"])
            # Si los datos modificados corresponden a un lugar ya registrado informa
            if str(placeSearch.id) != str(pk):
                data = {
                    'code': 'place_exists_error',
                    'message': 'El lugar ' + str(placeSearch) + ' ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si la modificacion realizada es correcta la registra
        except Place.DoesNotExist:
            serializer.save()
        return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        place = self.get_object()
        # Controla que el lugar a eliminar no pertenezca a una ruta activa
        placeInRoute = Route.objects.filter((Q(origin=kwargs.get('pk')) | Q(destination=kwargs.get('pk'))),
                                            delete=False)
        # Si pertenece a una ruta activa informa que no puede eliminar
        if placeInRoute:
            data = {
                'code': 'place_exists_in_route_error',
                'message': 'El lugar ' + place.__str__() + ' no se puede eliminar porque pertenece a una ruta activa'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no pertenece a una ruta activa realiza el marcado logico de borrado como un update
        place.delete = True
        serializer = PlaceListSerializer(place, data=place.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.filter(delete=False).order_by('origin__province', 'origin__town')
    serializer_class = RouteListSerializer

    @action(detail=False)
    def all(self, request):
        route = Route.objects.filter(delete=False)
        serializer = RouteListSerializer(route, many=True)
        return Response(serializer.data)  # status 200

    def create(self, request):
        routeData = request.data
        print(routeData)
        try:
            # Controla si la ruta a crear ya exista
            route = Route.objects.get(origin__id=routeData['origin'], destination__id=routeData['destination'],
                                      bus__id=routeData['bus'])
            # Si existe y esta borrada se reactiva actualizando sus datos
            if route.delete:
                route.delete = False
                route.distance = routeData['distance']
                route.duration = routeData['duration']
                serializer = RouteSerializer(route, data=route.__dict__, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200
            # Si existe y no esta borrada informa que ya ha sido registrada anteriormente
            data = {
                'code': 'route_exists_error',
                'message': 'La ruta ' + route.__str__() + ' que esta tratando de crear ya ha sido registrada con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Si no existe se registra como nueva ruta
        except Route.DoesNotExist:
            serializer = RouteSerializer(data=routeData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        routeData = request.data
        route = self.get_object()
        serializer = RouteSerializer(route, data=routeData, partial=True)
        serializer.is_valid(raise_exception=True)
        # Controla que la ruta a modificar no pertenezca a un viaje
        routeInTravel = Travel.objects.filter(route=pk, delete=False)
        if routeInTravel:
            data = {
                'code': 'route_exists_in_travel_error',
                'message': 'La ruta ' + str(route) + ' que esta tratando de modificar pertenece a un viaje'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Controla si la ruta modificada ya existe
            routeSearch = Route.objects.get(origin__id=routeData['origin'], destination__id=routeData['destination'],
                                            bus__id=routeData['bus'])
            # Si la encuentra informa que no se puede modificar porque ya existe anteriormente
            if str(routeSearch.id) != str(pk):
                data = {
                    'code': 'route_exists_error',
                    'message': 'La ruta ' + str(
                        routeSearch) + ' que esta tratando de modificar ya ha sido registrada con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data)  # status 200
        except Route.DoesNotExist:
            serializer.save()
            return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        route = self.get_object()
        # Controla que la ruta a eliminar no pertenezca a un viaje
        routeInTravel = Travel.objects.filter(route=kwargs.get('pk'), delete=False)
        if routeInTravel:
            data = {
                'code': 'route_exists_in_travel_error',
                'message': 'La ruta ' + str(route) + ' que esta tratando de eliminar pertenece a un viaje'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        # Realiza el borrado logico como un update
        route.delete = True
        serializer = RouteSerializer(route, data=route.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class TravelViewSet(viewsets.ModelViewSet):
    queryset = Travel.objects.filter(delete=False).order_by('departure_date')
    serializer_class = TravelListSerializer

    @action(detail=False)
    def all(self, request):
        travel = Travel.objects.filter(delete=False).order_by('departure_date')
        serializer = TravelListSerializer(travel, many=True)
        return Response(serializer.data)  # status 200

    @staticmethod
    # Calcula que no se solapeen los horarios de los viajes
    def is_date_overlap(departure1, departure2, arrival1, arrival2):
        departure1 = departure1.replace(tzinfo=timezone.utc)
        arrival1 = arrival1.replace(tzinfo=timezone.utc)
        time_range1 = DateTimeRange(departure1, arrival1)
        time_range2 = DateTimeRange(departure2, arrival2)
        # departure2 = departure2 - (arrival1 - departure1)
        # print("el resultado del calculo de fecha es" + str(departure2))
        result = time_range1.intersection(time_range2)
        return str(result) != 'NaT - NaT'

    @action(detail=False)
    # Devuelve el listado de viajes disponibles se necesita recibir por request body id de origin,
    # id de destination y fecha de salida(departure) en formato "YYYY-MM-DD"
    def get_available_travel(self, request):
        travel = Travel.objects.filter(route__origin=request.GET['origin'],
                                       route__destination=request.GET['destination'],
                                       departure_date__date=request.GET['departure'],
                                       delete=False, state='Pendiente', available_seats__gt=0).order_by(
            'departure_date')
        if not travel:
            data = {
                'code': 'travel_no_exists__error',
                'message': 'No hay viajes disponibles para esa ruta y fecha'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TravelListSerializer(travel, many=True)
        return Response(serializer.data)  # status 200

    @action(detail=False)
    # Devuelve el listado de viajes pendientes de un chofer determinado
    # enviar por parametro driver el id de usuario driver
    def get_travel_pending(self, request):
        travel = Travel.objects.filter(Q(state='Pendiente') | Q(state='Iniciado'),
                                       driver=request.GET['driver']).order_by('departure_date')
        if not travel:
            data = {
                'code': 'travel_no_exists_today_error',
                'message': 'No posee viajes pendientes'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TravelListSerializer(travel, many=True)
        return Response(serializer.data)  # status 200

    @action(detail=False)
    def get_all_travel_pending(self, request):
        travel = Travel.objects.filter(state='Pendiente').order_by('departure_date')
        if not travel:
            data = {
                'code': 'travel_no_exists_pending_error',
                'message': 'No existen viajes pendientes'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TravelListSerializer(travel, many=True)
        return Response(serializer.data)  # status 200



    @action(detail=False)
    # Devuelve el listado de viajes realizados por un chofer determinado
    # enviar por parametro driver el id del usuario driver
    def get_travel_over(self, request):
        travel = Travel.objects.filter(driver=request.GET['driver'], delete=False,
                                       state='Terminado').order_by('departure_date')
        if not travel:
            data = {
                'code': 'travel_no_exists_error',
                'message': 'No posee viajes realizados'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TravelListSerializer(travel, many=True)
        return Response(serializer.data)  # status 200

    @action(detail=False, methods=['post'])
    def finish_travel(self, request):
        travel = Travel.objects.get(id=request.data['travel'])
        travel.state = 'Terminado'
        travel.save()
        data = {
            'code': 'finish_travel',
            'message': 'El viaje se finalizo con exito'
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def init_travel(self, request):
        travel = Travel.objects.get(id=request.data['travel'])
        travel.state = 'Iniciado'
        travel.save()
        tickets = Ticket.objects.filter(travel=travel.id, state='Activo')
        for record in tickets:
            record.state = 'Ausente'
            record.save()
        data = {
            'code': 'init_travel',
            'message': 'El viaje se inicio con exito'
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def cancel_travel(self, request):
        travel = Travel.objects.get(id=request.data['travel'])
        travel.state = 'Cancelado'
        travel.save()
        tickets = Ticket.objects.filter(travel=travel.id)
        for record in tickets:
            record.state = 'Cancelado'
            record.amount_paid = 0
            record.save()
        data = {
            'code': 'cancel_travel',
            'message': 'El viaje se ha cancelado'
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def create(self, request):
        travelData = request.data
        # Controla que no se solapeen los horarios
        travelList = list(filter(
            lambda travel: self.is_date_overlap(datetime.strptime(travelData['departure_date'], "%d-%m-%Y %H:%M"),
                                                travel.departure_date,
                                                datetime.strptime(travelData['arrival_date'], "%d-%m-%Y %H:%M"),
                                                travel.arrival_date),
            Travel.objects.filter(route__id=travelData['route'], delete=False)))
        if travelList:
            data = {
                'code': 'travel_exists_error',
                'message': 'El viaje que esta tratando de registrar ya existe en esos horarios'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        travelData['departure_date'] = datetime.strptime(travelData['departure_date'], "%d-%m-%Y %H:%M").replace(
            tzinfo=timezone.utc)
        travelData['arrival_date'] = datetime.strptime(travelData['arrival_date'], "%d-%m-%Y %H:%M").replace(
            tzinfo=timezone.utc)
        route = Route.objects.get(id=travelData['route'])
        user = User.objects.get(username=route.driver.email)
        travelData['driver'] = user.id
        travelData['available_seats'] = route.bus.seatNumbers
        serializer = TravelSerializer(data=travelData)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        travelData = request.data
        travel = self.get_object()
        # Controla que no haya pasajes vendidos
        travelInTicket = Ticket.objects.filter(travel=pk, delete=False)
        if travelInTicket:
            data = {
                'code': 'travel_exists_in_ticket_error',
                'message': 'El viaje que esta tratando de modificar posee pasajes vendidos'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        travelList = list(filter(
            lambda travel_l: self.is_date_overlap(datetime.strptime(travelData['departure_date'], "%d-%m-%Y %H:%M"),
                                                  travel_l.departure_date,
                                                  datetime.strptime(travelData['arrival_date'], "%d-%m-%Y %H:%M"),
                                                  travel_l.arrival_date),
            Travel.objects.filter(~Q(id=pk), route__id=travelData['route'], delete=False)))
        if travelList:
            data = {
                'code': 'travel_exists_error',
                'message': 'El viaje que esta tratando de modificar ya existe en esos horarios'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        travelData['departure_date'] = datetime.strptime(travelData['departure_date'], "%d-%m-%Y %H:%M").replace(
            tzinfo=timezone.utc)
        travelData['arrival_date'] = datetime.strptime(travelData['arrival_date'], "%d-%m-%Y %H:%M").replace(
            tzinfo=timezone.utc)
        route = Route.objects.get(id=travelData['route'])
        user = User.objects.get(username=route.driver.email)
        travelData['driver'] = user.id
        travelData['available_seats'] = route.bus.seatNumbers
        serializer = TravelSerializer(travel, data=travelData, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        travel = self.get_object()
        # Realiza el borrado logico como un update si no tiene pasajes vendidos
        travelInTicket = Ticket.objects.filter(travel=kwargs.get('pk'), delete=False)
        if travelInTicket:
            data = {
                'code': 'travel_exists_in_ticket_error',
                'message': 'El viaje que esta tratando de eliminar posee pasajes vendidos'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        travel.delete = True
        travel.state = 'Cancelado'
        serializer = TravelSerializer(travel, data=travel.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.filter(delete=False)
    serializer_class = ProfileSerializer

    def create(self, request):
        profileData = request.data
        try:
            user = User.objects.get(username=profileData["username"])
            data = {
                'code': 'profile_exists_error',
                'message': 'El usuario ' + user.username + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            rol = Group.objects.get(name='CLIENT')
            userNew = User.objects.create_user(username=profileData["username"], email=profileData["email"],
                                               password=profileData["password"], last_name=profileData["lastname"],
                                               first_name=profileData["firstname"])
            rol.user_set.add(userNew)
            if 'card_holder' in profileData:
                profile = Profile.objects.create(user=userNew, idCards=profileData["idCards"],
                                                 birth_date=profileData["birth_date"], phone=profileData["phone"],
                                                 card_holder=profileData["card_holder"],
                                                 card_number=profileData["card_number"],
                                                 month_exp=profileData["month_exp"], year_exp=profileData["year_exp"],
                                                 security_code=profileData["security_code"])
            else:
                profile = Profile.objects.create(user=userNew, idCards=profileData["idCards"],
                                                 birth_date=profileData["birth_date"], phone=profileData["phone"])

            profile.save()
            serializer = ProfileSerializer(data=profile.__dict__)
            serializer.is_valid(raise_exception=False)
            # serializer.save()
            return Response(serializer.data)  # status 200

    @transaction.atomic
    def update(self, request, pk=None):
        profileData = request.data
        profile = self.get_object()
        user = User.objects.get(username=profileData["username"])
        user.first_name = profileData["firstname"]
        user.last_name = profileData["lastname"]
        user.save()
        profile.idCards = profileData["idCards"]
        profile.birth_date = profileData["birth_date"]
        profile.phone = profileData["phone"]
        if 'card_holder' in profileData:
            profile.card_holder = profileData["card_holder"]
            profile.card_number = profileData["card_number"]
            profile.month_exp = profileData["month_exp"]
            profile.year_exp = profileData["year_exp"]
            profile.security_code = profileData["security_code"]
        profile.save()
        serializer = ProfileSerializer(data=profile.__dict__)
        serializer.is_valid(raise_exception=False)
        # serializer.save()
        return Response(serializer.data)  # status 200

    @action(detail=False, methods=['post'])
    def unsubscribe_gold(self, request):
        # Se necesita recibir el id del usuario.
        profile = Profile.objects.get(user=request.data['user'])
        profile.card_holder = None
        profile.card_number = None
        profile.month_exp = None
        profile.year_exp = None
        profile.security_code = None
        profile.save()
        data = {
            'code': 'unsubscribe',
            'message': 'La desuscripci??n GOLD ha sido exitosa'
        }
        return Response(data=data, status=status.HTTP_200_OK)


class RolViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    @action(detail=False)
    def get_roles_by_user(self, request):
        user = User.objects.get(username=request.GET['username'])
        serializer = RolSerializer(user.groups, many=True)
        return Response(serializer.data)  # status 200


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    @action(detail=False, methods=['post'])
    def sign_in(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None:
            if user.groups.get().name == 'CLIENT':
                profile = Profile.objects.get(user=user.id)
                serializer = ProfileSignSerializer(profile)
            else:
                serializer = UserSignSerializer(user)
            return Response(serializer.data)  # status 200
        else:
            data = {
                'code': 'authenticate_error',
                'message': 'Usuario o Clave Incorrecta'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        user = User.objects.get(id=request.data['user'])
        user.set_password(request.data['password'])
        user.save()
        data = {
            'code': 'password_change',
            'message': 'La Contrase??a se ha modificado correctamente'
        }
        return Response(data=data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def view_profile(self, request):
        user = User.objects.get(username=request.data['username'])
        if user.groups.get().name != 'ADMIN':
            profile = Profile.objects.get(user=user.id)
            serializer = ProfileSerializer(profile)
        else:
            serializer = UserSerializer(user)
        return Response(serializer.data)  # status 200

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        tickets = Ticket.objects.filter(user=user.id, state='Activo')
        if tickets:
            data = {
                'code': 'ticket_exists_error',
                'message': 'El usuario posee pasajes activos no puede darse de baja'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        profile = Profile.objects.get(user=user.id)
        profile.delete = True
        profile.save()
        user.is_active = False
        user.save()
        data = {
            'code': 'password_change',
            'message': 'El Usuario ' + user.username + ' ha sido dado de baja exitosamente'
        }
        return Response(data=data, status=status.HTTP_200_OK)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.filter(delete=False)
    serializer_class = TicketSerializer

    @action(detail=False)
    # Devuelve el listado de tickets rechazados
    def get_ticket_rejected(self, request):
        tickets = Ticket.objects.filter(state='Rechazado', delete=False).order_by('-travel__departure_date')
        if not tickets:
            data = {
                'code': 'ticjets_no_exists_error',
                'message': 'No hay tickets rechazados'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TicketRejectedSerializer(tickets, many=True)
        return Response(serializer.data)  # status 200

    @transaction.atomic
    def create(self, request):
        # Registra la venta del pasaje si tiene lugar disponible
        list_supplies = request.data["suppliesId"]
        ticketData = request.data
        travel = Travel.objects.get(id=ticketData['travel'])
        user = User.objects.get(id=ticketData['user'])
        ticket = Ticket(idCards=ticketData['idCards'], birth_date=ticketData['birth_date'],
                        phone=ticketData['phone'], firstName=ticketData['firstName'],
                        lastName=ticketData['lastName'], email=ticketData['email'],
                        travel=travel, buy_date=datetime.today(), user=user, amount_paid=ticketData['amount_paid'])
        if travel.available_seats <= 0:
            data = {
                'code': 'not_seats_error',
                'message': 'No hay lugares disponibles'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        ticket.save()
        travel.available_seats -= 1
        travel.ticket_sold += 1
        travel.save()
        for record in list_supplies:
            supplies = Supplies.objects.get(id=record['id'])
            supplies_detail = SuppliesDetail.objects.create(supplies=supplies, ticket=ticket,
                                                            quantity=record['quantity'], price=record['price'])
            supplies_detail.save()
        return Response(json.dumps(model_to_dict(ticket), sort_keys=True, default=str))  # status 200

    @action(detail=False)
    # Devuelve el listado de ticket de viajes adquiridos por un usuario
    def get_my_travels(self, request):
        tickets = Ticket.objects.filter(user=request.GET['user']).order_by('travel__departure_date')
        if not tickets:
            data = {
                'code': 'ticket_no_exists__error',
                'message': 'El usuario no posee pasajes adquiridos'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)  # status 200

    @action(detail=False)
    # Devuelve el listado de tickets de un viaje determinado
    # Enviar por parametro en travel el id  del viaje
    def get_tickets_travel(self, request):
        tickets = Ticket.objects.filter(~Q(state='Devuelto') & ~Q(state='Cancelado'),
                                        travel=request.GET['travel']).order_by('id')
        if not tickets:
            data = {
                'code': 'ticket_no_exists__error',
                'message': 'No hay pasajes vendidos para este viaje'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)  # status 200

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def test_result(self, request):
        ticket = Ticket.objects.get(id=request.data["ticket"])
        state = request.data["state"]
        if state == 'Aceptado':
            ticket.state = 'Aceptado'
            ticket.save()
            data = {
                'code': 'test_register_ok',
                'message': 'Test negativo. El Pasajero ha sido Aceptado'
            }
        elif state == 'Rechazado':
            profile = Profile.objects.get(user=ticket.user)
            profile.end_date_suspension = ticket.travel.departure_date + timedelta(days=15)
            profile.save()
            tickets_user = Ticket.objects.filter(~Q(state='Devuelto') & ~Q(state='Cancelado'),
                                                 user=ticket.user,
                                                 travel__departure_date__gte=ticket.travel.departure_date,
                                                 travel__departure_date__date__lte=profile.end_date_suspension.date(),
                                                 delete=False)
            for record in tickets_user:
                record.state = 'Rechazado'
                record.amount_paid = record.amount_paid / 2
                record.save()

            data = {
                'code': 'test_register_no',
                'message': 'Test positivo. El Pasajero ha sido Rechazado por riesgoso'
            }
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def return_ticket(self, request):
        ticket = Ticket.objects.get(id=request.data["ticket"])
        if (ticket.travel.state != 'Pendiente') or (ticket.state != 'Activo'):
            data = {
                'code': 'ticket_return__error',
                'message': 'El pasaje no puede ser devuelto'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        departure_date = ticket.travel.departure_date
        today = datetime.today().replace(tzinfo=timezone.utc)
        difference = departure_date - today
        if difference.days >= 2:
            data = {
                'code': 'ticket_total_return__error',
                'message': 'Se registro la devoluc??on del pasaje antes de las 48hs de la fecha del viaje. Se vera'
                           ' reflejado en su proximo resumen un reintegro de $ ' + str(ticket.amount_paid) + ' '
                                                                                                             'correspondiente al 100% de lo abonado '
            }
            ticket.amount_paid = 0
        else:
            if difference.days >= 0:
                data = {
                    'code': 'ticket_partial_return__error',
                    'message': 'Se registro la devoluc??on del pasaje dentro de las 48hs de la fecha del viaje. Se vera'
                               ' reflejado en su proximo resumen un reintegro de $ ' + str(ticket.amount_paid / 2) + ' '
                                                                                                                     'correspondiente al 50% de lo abonado.'
                }
                ticket.amount_paid = ticket.amount_paid / 2
            else:
                data = {
                    'code': 'ticket_no_exists__error',
                    'message': 'El pasaje no puede ser devuelto'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        # Volver a agregar 1 asiento disponible en el viaje
        travel = Travel.objects.get(id=ticket.travel.id)
        travel.available_seats += 1
        travel.ticket_sold -= 1
        travel.save()
        ticket.state = 'Devuelto'
        ticket.save()
        return Response(data=data, status=status.HTTP_200_OK)

    @transaction.atomic
    @action(detail=False, methods=['post'])
    def simple_buy(self, request):
        email = request.data["username"]
        user = User.objects.filter(username=email)
        if not user:
            rol = Group.objects.get(name='CLIENT')
            user = User.objects.create_user(username=email, email=email,
                                            password=email)
            rol.user_set.add(user)
            profile = Profile.objects.create(user=user)
            profile.save()
        user = User.objects.get(username=email)
        travel = Travel.objects.get(id=request.data['travel'])
        profile = Profile.objects.get(user=user.id)
        ticket = Ticket(idCards=profile.idCards, birth_date=profile.birth_date,
                        phone=profile.phone, firstName=user.first_name,
                        lastName=user.last_name, email=email,
                        travel=travel, buy_date=datetime.today(), user=user, amount_paid=travel.price)
        ticket.save()
        travel.available_seats -= 1
        travel.ticket_sold += 1
        travel.save()
        return Response(json.dumps(model_to_dict(ticket), sort_keys=True, default=str))  # status 200


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(delete=False).order_by('-date')
    serializer_class = CommentSerializer

    @action(detail=False)
    def all(self, request):
        comment = Comment.objects.filter(delete=False).order_by('-date')
        comment = comment[:10]
        serializer = CommentListSerializer(comment, many=True)
        return Response(serializer.data)  # status 200

    def create(self, request):
        commentData = request.data
        userInTicket = Ticket.objects.filter(user=commentData['user'], delete=False)
        if not userInTicket:
            data = {
                'code': 'not_ticket_error',
                'message': 'Estimado usuario para poder comentar se necesita haber adquirido al menos un pasaje'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        serializer = CommentSerializer(data=commentData)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        commentData = request.data
        comment = self.get_object()
        comment.date = datetime.today()
        serializer = CommentSerializer(comment, data=commentData, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete = True
        serializer = CommentSerializer(comment, data=comment.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200
