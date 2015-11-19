import datetime
from django.db import models


class TaxiLocation(models.Model):
    taxi_id = models.CharField(max_length=200, unique=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)


class PassengerOrder(models.Model):
    passenger_id = models.CharField(max_length=200, unique=True, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    time_to_pick_up = models.DateTimeField(null=True, blank=True, db_index=True, default=datetime.datetime.now)
    taxi_id = models.CharField(max_length=200, null=True, blank=True, unique=True, db_index=True, default=None)