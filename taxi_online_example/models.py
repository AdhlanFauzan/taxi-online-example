# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from taxi_online_example.utils import date_now_or_future_validator


class TaxiLocation(models.Model):
    taxi_id = models.CharField(max_length=200, unique=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, db_index=True,
                              validators=[MinValueValidator(-180),
                                          MaxValueValidator(180)])
    lat = models.DecimalField(max_digits=9, decimal_places=6, db_index=True,
                              validators=[MinValueValidator(-90),
                                          MaxValueValidator(90)])
    is_busy = models.BooleanField(default=False)

    def change_activity(self, is_busy):
        self.is_busy = is_busy
        self.save()


class PassengerOrder(models.Model):
    passenger_id = models.CharField(max_length=200, unique=True, db_index=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6,
                              validators=[MinValueValidator(-180),
                                          MaxValueValidator(180)])
    lat = models.DecimalField(max_digits=9, decimal_places=6,
                              validators=[MinValueValidator(-90),
                                          MaxValueValidator(90)])
    time_to_pick_up = models.DateTimeField(null=True, blank=True, db_index=True, default=datetime.datetime.now,
                                           validators=[date_now_or_future_validator])
    taxi_id = models.CharField(max_length=200, null=True, blank=True, unique=True, db_index=True, default=None)

    def is_waiting_for_taxi(self):
        return True if self.taxi_id else False

    def remove_taxi(self):
        self.taxi_id = None
        self.save()

    def get_all_passengers_for_pick_up(self):
        pass

    def get_nearest_free_taxi(self, radius=10):
        # http://www.plumislandmedia.net/mysql/haversine-mysql-nearest-loc/
        sql = """SELECT tl.taxi_id,
                        p.distance_unit
                                 * DEGREES(ACOS(COS(RADIANS(p.latpoint))
                                 * COS(RADIANS(tl.lat))
                                 * COS(RADIANS(p.longpoint) - RADIANS(tl.lon))
                                 + SIN(RADIANS(p.latpoint))
                                 * SIN(RADIANS(tl.lat)))) AS distance_in_km
                  FROM %(taxi_location_table_name)s AS tl
                  JOIN ( /* these are the query parameters */
                        SELECT %(latpoint)s AS latpoint,
                               %(longpoint)s AS longpoint,
                               %(radius)s AS radius,
                               111.045 AS distance_unit
                    ) AS p ON 1=1
                  WHERE tl.is_busy = false
                    AND tl.lat
                      BETWEEN p.latpoint  - (p.radius / p.distance_unit)
                          AND p.latpoint  + (p.radius / p.distance_unit)
                    AND tl.lon
                      BETWEEN p.longpoint - (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
                          AND p.longpoint + (p.radius / (p.distance_unit * COS(RADIANS(p.latpoint))))
                  ORDER BY distance_in_km
                  LIMIT 10""" % {'taxi_location_table_name': TaxiLocation._meta.db_table,
                                 'latpoint': self.lat, 'longpoint': self.lon, 'radius': radius}

        return TaxiLocation.objects.raw(sql)





