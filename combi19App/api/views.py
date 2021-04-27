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
   #permission_classes = [IsAuthenticated]


    def create(self, request):
        suppliesData = request.data
        try:
            supplies = Supplies.objects.get(description=suppliesData["description"])
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
        serializer = SuppliesSerializer(supplies, data=suppliesData)
        serializer.is_valid(raise_exception=True)

        try:
            suppliesSearch = Supplies.objects.get(description=suppliesData["description"])
            if str(suppliesSearch.id) != str(pk):
                data = {
                    'code': 'supplies_exists_error',
                    'message': 'El insumo ' + supplies.description + ' ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)  # status 200
        except Supplies.DoesNotExist:
            serializer.save()
            return Response(serializer.data) #status 200




    def destroy(self, request, *args, **kwargs):
        supplies = self.get_object()
        supplies.delete = True
        serializer = SuppliesSerializer(supplies, data=supplies.__dict__)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200




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


    def update(self, request, pk=None):
        placeData = request.data
        place = self.get_object()
        serializer = PlaceSerializer(place, data=placeData)
        serializer.is_valid(raise_exception=True)
        #Faltaria controlar que el lugar a modificar no este asignado a una ruta (origen/destino)
        try:
            placeSearch = Place.objects.get(town=placeData["town"], province=placeData["province"])
            if str(placeSearch.id) != str(pk):
                data = {
                    'code': 'place_exists_error',
                    'message': 'El lugar ' + place.__str__() + ' ya ha sido registrado con anterioridad'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data)  # status 200
        except Place.DoesNotExist:
            serializer.save()
            return Response(serializer.data) #status 200


    def destroy(self, request, *args, **kwargs):
        # Falta agregar la validación de que no exista este lugar en una ruta tanto en origen como en destino
        place = self.get_object()
        place.delete = True
        print(place)
        serializer = PlaceSerializer(place, data=place.__dict__)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)  # status 200












