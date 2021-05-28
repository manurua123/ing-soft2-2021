# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


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
    idCards = models.IntegerField(null=True)
    birth_date = models.DateField(null=True)
    fullName = models.CharField(max_length=120, null=False, default='')
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.fullName


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
    duration = models.TimeField(null=False)
    distance = models.IntegerField(null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0} / {1} con Combi {2}"
        return txt.format(self.origin.__str__(), self.destination.__str__(), self.bus.__str__())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    idCards = models.IntegerField(null=True)
    birth_date = models.DateField(null=True)
    phone = models.CharField(max_length=20)
    card_holder = models.CharField(max_length=50, null=True)
    card_number = models.IntegerField(null=True)
    month_exp = models.IntegerField(null=True)
    year_exp = models.IntegerField(null=True)
    security_code = models.CharField(max_length=3, null=True)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.phone


class Travel(models.Model):
    route = models.ForeignKey(Route, on_delete=models.RESTRICT)
    departure_date = models.DateTimeField(null=False)
    arrival_date = models.DateTimeField(null=False)
    price = models.FloatField(null=False)
    available_seats = models.IntegerField(null=False)
    stateChoice = [('Pendiente', 'Pendiente'), ('Iniciado', 'Iniciado'),
                   ('Terminado', 'Terminado'), ('Cancelado', 'Cancelado')]
    state = models.CharField(max_length=10, choices=stateChoice, default='Pendiente', null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        txt = "{0} el día {1}"
        return txt.format(self.route.__str__(), self.departure_date)


class Ticket(models.Model):
    supplies = models.ManyToManyField(Supplies, through="SuppliesDetail")
    travel = models.ForeignKey(Travel, on_delete=models.RESTRICT)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    buy_date = models.DateField(null=False)
    idCards = models.IntegerField(null=False)
    birth_date = models.DateField(null=False)
    phone = models.CharField(max_length=20)
    firstName = models.CharField(max_length=60, null=False)
    lastName = models.CharField(max_length=60, null=False)
    email = models.EmailField(null=False)
    stateChoice = [('Activo', 'Activo'), ('Rechazado', 'Rechazado'), ('Cancelado', 'Cancelado')]
    state = models.CharField(max_length=9, choices=stateChoice, default='Activo', null=False)
    delete = models.BooleanField(default=False)

    def __str__(self):
        return self.firstName


class SuppliesDetail(models.Model):
    supplies = models.ForeignKey('Supplies', on_delete=models.RESTRICT)
    ticket = models.ForeignKey('Ticket', on_delete=models.RESTRICT)
    quantity = models.IntegerField(null=False)
    price = models.FloatField(null=False)


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.RESTRICT)
    text = models.TextField(null=False)
    date = models.DateTimeField(default=datetime.now())
    delete = models.BooleanField(default=False)
