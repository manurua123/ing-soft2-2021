# Create your models here.
from django.db import models

# Soy César Amiconi prueba
class Supplies(models.Model):
    description = models.CharField(max_length=60, unique=True, error_messages={'unique': "El insumo ya ha sido "
                                                                                         "registrado con "
                                                                                         "anterioridad."})
    ddd = models.CharField(max_length=60, default='0000000')
    price = models.FloatField(null=False)

    def __str__(self):
        return self.description

class Driver(models.Model):
    firstName = models.CharField(max_length=60, null=False)
    lastName = models.CharField(max_length=60, null=False)
    email = models.EmailField(unique=True, error_messages={'unique': "El chofer ya ha sido  "
                                                                                       "registrado con "
                                                                                       "anterioridad."})
    phone = models.IntegerField(null=False)
    fullName = models.CharField(max_length=120, null=False, default='')


    def __str__(self):
        return self.email

class Bus(models.Model):
    identification = models.CharField(max_length=5,unique=True, error_messages={'unique':"El vehículo ya ha sido  "
                                                                                       "registrado con "
                                                                                       "anterioridad."  })
    model = models.CharField(max_length=30, null=False)
    licencePlate = models.CharField(max_length=7, null=False)
    seatNumbers = models.IntegerField(null=False)
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT)
    type = models.CharField(max_length=15, null=False)

    def __str__(self):
        return self.identification

class Place(models.Model):
    town = models.CharField(max_length=50, null=False)
    province =models.CharField(max_length=25, null=False)

    def __str__(self):
        txt = "{0} - {1}"
        return txt.format(self.town, self.province)

class Route(models.Model):

    identification = models.IntegerField(max_length=60, unique=True, error_messages={'unique': "La ruta ya ha sido "
                                                                                         "registrado con "
                                                                                         "anterioridad."})
    origin = models.CharField(max_length=50, null=False)
    destiny = models.CharField(max_length=50, null=False)
    bus = models.ForeignKey(Bus, on_delete=models.RESTRICT)
    duration = models.IntegerField(null=False)
    distance = models.IntegerField(null=False)



    def __str__(self):
        return txt.format(self.origin, self.destiny, self.bus, self.duration,self.distance)