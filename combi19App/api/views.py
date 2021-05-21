from django.contrib.auth.decorators import login_required
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User, Group

from .serializers import SuppliesSerializer, DriverSerializer, BusSerializer, PlaceListSerializer, RouteSerializer, \
    RouteListSerializer, BusListSerializer, PlaceSerializer, ProfileSerializer, RolSerializer
from .models import Supplies, Driver, Bus, Place, Route, Profile
from rest_framework.response import Response
from django.db.models import Q


class SuppliesViewSet(viewsets.ModelViewSet):
    queryset = Supplies.objects.all().order_by('description')
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
                'message': 'El correo electrónico: ' + driver.email + ' ya se encuentra registrado.'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Driver.DoesNotExist:
            data = {
                'code': 'driver_update_not_exists',
                'message': 'No existe el chofer que esta tratando de modificar'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        driver = self.get_object()
        # Controla que el chofer a eliminar no pertenezca a una combi activa
        driverInBus = Bus.objects.filter(driver=kwargs.get('pk'), delete=False)
        # Si pertenece a una Combi activa informa que no puede eliminar
        if driverInBus:
            data = {
                'code': 'driver_exists_in_bus_error',
                'message': 'El chofer ' + driver.__str__() + ' no se puede eliminar porque existe en un vehículo Activo'
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
            # Controla si el vehículo a crear ya existe

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
            # Si no existe Busca que el chofer no este ya registrado en un vehículo
            driverInBus = Bus.objects.filter(driver=busData['driver'], delete=False)
            if driverInBus:
                data = {
                    'code': 'driver_exists_in_bus_error',
                    'message': 'El chofer ' + driverInBus[0].driver.__str__() + ' ya está registrado en otro vehículo'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            #Crea un nuevo vehículo
            serializer = BusSerializer(data=busData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)  # status 200

    def update(self, request, pk=None):
        busData = request.data
        bus = self.get_object()

        try:

            # Controla si la combi modificada ya existe
            busSearch = Bus.objects.get(identification=busData['identification'])
            # Si la encuentra informa que no se puede modificar porque ya existe anteriormente
            if str(busSearch.id) != str(pk):
                data = {
                    'code': 'bus_exists_error',
                    'message': 'El vehículo ' + str(
                        busSearch) + ' que esta tratando de modificar ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            driverInBus = Bus.objects.filter(driver=busData['driver'], delete=False)

            if driverInBus and str(bus.driver) != str(driverInBus[0].driver):
                data = {
                    'code': 'driver_exists_in_bus_error',
                    'message': 'El chofer ' + driverInBus[0].driver.__str__() + ' ya está registrado en otro vehículo'
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
                'message': 'El vehículo ' + bus.__str__() + ' no se puede eliminar porque existe en una ruta activa'
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
            # Si existe pero no esta borrado informa que ya está anteriormente registrado
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

    def create(self, request):
        routeData = request.data
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
        # Atención!!! Faltaria controlar que no este asignada a un viaje
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
        # Atencion!!! Falta agregar la validación de que no exista esta ruta en un viaje
        # Realiza el borrado logico como un update
        route.delete = True
        serializer = RouteSerializer(route, data=route.__dict__, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.filter(delete=False)
    serializer_class = ProfileSerializer

    @action(detail=False)
    def all(self, request):
        user = User.objects.create_user(username='Cesar2', email='cesar.amiconi@hotmail.com', password='44hhd')
        profile = Profile.objects.create(user=user, idCards=249531655, birth_date='2021-04-08', phone='734784347')
        profile.save()
        return Response('ok')  # status 200

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
                                               password=profileData["password"])
            rol.user_set.add(userNew)
            profile = Profile.objects.create(user=userNew, idCards=profileData["idCards"],
                                             birth_date=profileData["birth_date"], phone=profileData["phone"])

            profile.save()
            serializer = ProfileSerializer(data=profile.__dict__)
            serializer.is_valid(raise_exception=False)
            # serializer.save()
            return Response(serializer.data)  # status 200


class RolViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    @action(detail=False)
    def get_roles_by_user(self, request):
        user = User.objects.get(username=request.GET['username'])
        serializer = RolSerializer(user.groups, many=True)

        return Response(serializer.data)  # status 200
