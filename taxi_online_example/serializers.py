# -*- coding: utf-8 -*-

import datetime
from rest_framework import serializers
from taxi_online_example.models import TaxiLocation, PassengerOrder
from taxi_online_example.utils import UnixEpochDateField, date_now_or_future_validator


class TaxiLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxiLocation
        fields = ('taxi_id', 'lon', 'lat')

    def create(self, validated_data):
        return TaxiLocation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.lon = validated_data.get('lon', instance.lon)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.save()
        return instance


class PassengerOrderSerializer(serializers.ModelSerializer):
    time_to_pick_up = UnixEpochDateField(required=False, default=datetime.datetime.now,
                                         validators=[date_now_or_future_validator])

    class Meta:
        model = PassengerOrder
        fields = ('passenger_id', 'lon', 'lat', 'time_to_pick_up')

    def create(self, validated_data):
        return PassengerOrder.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.lon = validated_data.get('lon', instance.lon)
        instance.lat = validated_data.get('lat', instance.lat)
        instance.time_to_pick_up = validated_data.get('time_to_pick_up', instance.time_to_pick_up)
        instance.save()
        return instance