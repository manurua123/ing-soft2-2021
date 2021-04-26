from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from .serializers import SuppliesSerializer, DriverSerializer, BusSerializer, PlaceSerializer, RouteSerializer
from .models import Supplies, Driver, Bus, Place, Route
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.permissions import IsAuthenticated


class SuppliesViewSet(viewsets.ModelViewSet):
    queryset = Supplies.objects.all().order_by('description')
    serializer_class = SuppliesSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Supplies.objects.all().order_by('description')
        serializer = SuppliesSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Supplies.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = SuppliesSerializer(user)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        print(instance)
        try:
            sc = Supplies.objects.get(id=3)
            print(sc)
            return Response({'message': 'El chofer que está tratando de eliminar tiene una combi asignada'}, status=400)

        except ObjectDoesNotExist:
            instance.delete()

    #        instance.delete()
    #        print(instance.price)

    def create(self, request):
        print("esta creando gato")
        serializer = SuppliesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        print("destruyendo")
        try:
            instance = self.get_object()
            print(instance)
            print(instance.price)
            print(instance.id)
            # self.perform_destroy(instance)
        except Http404:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def save(self, request, pk=None):
        print(pk)
        queryset = Supplies.objects.all()
        serializer = SuppliesSerializer(queryset, many=True)
        return Response(serializer.data)

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all().order_by('firstName')
    serializer_class = DriverSerializer

    def create(self, request):
        driverData = request.data
        try:
            driver = Driver.objects.get(email=driverData["email"])
            data = {
                'code': 'driver_exists_error',
                'message': 'El chofer ' + driver.fullName + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Driver.DoesNotExist:
            driverData["fullName"] = driverData["lastName"] + ', ' + driverData["firstName"]
            serializer = DriverSerializer(data=driverData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data) #status 200

    def update(self, request, pk=None):
        driverData = request.data
        try:
            driver = Driver.objects.get(email=driverData["email"])
            if str(driver.id) == str(pk):
                driverData["fullName"] = driverData["lastName"] + ', ' + driverData["firstName"]
                serializer = DriverSerializer(driver,data=driverData, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200

            data = {
                'code': 'driver_update_already_exists',
                'message': 'Ya se encuentra registrado otro chofer con el mismo correo electronico: ' + driver.email
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
        try:
            bus = Bus.objects.get(driver=driver.id)
            data = {
                'code': 'driver_exists_error',
                'message': 'No se puede eliminar el chofer ya que el mismo figura como conductor en el vehiculo con patente: ' + bus.licencePlate,
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Bus.DoesNotExist:
            self.perform_destroy(driver)
            serializer = DriverSerializer(data=driver)
            return Response(data=serializer, status=status.HTTP_200_OK)

class BusViewSet(viewsets.ModelViewSet):
    queryset = Bus.objects.all().order_by('identification')
    serializer_class = BusSerializer

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all().order_by('province', 'town')
    serializer_class = PlaceSerializer

    def create(self, request):
        placeData = request.data
        try:
            place = Place.objects.get(town=placeData["town"], province=placeData["province"])
            data = {
                'code': 'place_exists_error',
                'message': 'El lugar ' + place.__str__() + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Place.DoesNotExist:
            serializer = PlaceSerializer(data=placeData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)#status 200
    """
    def update(self, request, pk=None):
        placeData = request.data
        try:
            place = Place.objects.get(town=placeData["town"], province=placeData["province"])
            data = {
                'code': 'place_exists_error',
                'message': 'El lugar ' + place.__str__() + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Place.DoesNotExist:
            serializer = PlaceSerializer(data=placeData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data) #status 200
    """

class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().order_by('identification')
    serializer_class = RouteSerializer

    def create(self, request):
        routeData = request.data
        try:
            route = Route.objects.get(identification=routeData["identification"])
            data = {
                'code': 'Route_exists_error',
                'message': 'La Ruta ' + route.identification + ' ya ha sido registrado con anterioridad'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Route.DoesNotExist:
            serializer = RouteSerializer(data=routeData)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data) #status 200
"""
    def update(self, request, pk=None):
        routeData = request.data
        try:
            route = Route.objects.get(identification=routeData["identification"])
            if str(route.identification) == str(pk):
                serializer = RouteSerializer(route,data=routeData, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)  # status 200

            data = {
                'code': 'route_update_already_exists',
                'message': 'Ya se encuentra registrado una ruta con el id: ' + route.identification
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        except Route.DoesNotExist:
            data = {
                'code': 'route_update_not_exists',
                'message': 'No existe la ruta que esta tratando de modificar'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
"""













