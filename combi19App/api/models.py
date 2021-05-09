# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Supplies(models.Model):
    description = models.CharField(max_length=60, unique=True, error_messages={'unique': "El insumo ya ha sido "
                                                                                         "registrado con "
                                                                                         "anterioridad."})
    price = models.FloatField(null=False)
    delete = models.BooleanField(default=False)

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
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.email


class Bus(models.Model):
    identification = models.CharField(max_length=5, unique=True, error_messages={'unique': "El vehículo ya ha sido  "
                                                                                           "registrado con "
                                                                                           "anterioridad."})
    model = models.CharField(max_length=30, null=False)
    licencePlate = models.CharField(max_length=7, null=False)
    seatNumbers = models.IntegerField(null=False)
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT)
    typeChoice = [('C', 'Cómoda'), ('SC', 'Super-Cómoda')]
    type = models.CharField(max_length=2, choices=typeChoice, null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.identification


class Place(models.Model):
    town = models.CharField(max_length=50, null=False)
    province = models.CharField(max_length=25, null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0} - {1}"
        return txt.format(self.town, self.province)


class Route(models.Model):
    origin = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='origen')
    destination = models.ForeignKey(Place, on_delete=models.RESTRICT, related_name='destino')
    bus = models.ForeignKey(Bus, on_delete=models.RESTRICT)
    duration = models.IntegerField(null=False)
    distance = models.IntegerField(null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0} / {1} con Combi {2}"
        return txt.format(self.origin.__str__(), self.destination.__str__(), self.bus.__str__())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idCards = models.IntegerField
    birth_date = models.DateField
    phone = models.CharField(max_length=20)
    card_holder = models.CharField(max_length=50, null=True)
    card_number = models.IntegerField
    month_exp = models.IntegerField
    year_exp = models.IntegerField
    security_code = models.CharField
    delete = models.BooleanField(default=False)

    def __str__(self):
        return phone


class Profiles(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idCards = models.IntegerField(null=False)
    birth_date = models.DateField(null=False)
    phone = models.CharField(max_length=20)
    card_holder = models.CharField(max_length=50, null=True)
    card_number = models.IntegerField(null=True)
    month_exp = models.IntegerField(null=True)
    year_exp = models.IntegerField(null=True)
    security_code = models.CharField(null=True)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return phone
