# -*- coding: utf-8 -*-

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser, JSONParser
from rest_framework import status
from taxi_online_example.models import TaxiLocation, PassengerOrder
from taxi_online_example.serializers import TaxiLocationSerializer, PassengerOrderSerializer
from django.template import loader
from django.http import HttpResponse, QueryDict


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({}))


class TaxiLocationAPI(APIView):
    """
    API for the taxi drivers: for sending to server information about current location and availability to pick up some passengers
    """

    parser_classes = (FormParser, JSONParser,)

    @staticmethod
    def get_object(pk, rise_exception=True):
        try:
            return TaxiLocation.objects.get(taxi_id=pk)
        except TaxiLocation.DoesNotExist:
            if rise_exception:
                raise Http404
            else:
                return False

    def get(self, request, pk, format=None):
        taxi = self.get_object(pk)
        serializer = TaxiLocationSerializer(taxi)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        data = request.data.dict() if isinstance(request.data, QueryDict) else request.data
        data['taxi_id'] = pk

        taxi = self.get_object(pk, rise_exception=False)
        if taxi:
            serializer = TaxiLocationSerializer(taxi, data=data)
            st = status.HTTP_200_OK
        else:
            serializer = TaxiLocationSerializer(data=data)
            serializer.key = pk
            st = status.HTTP_201_CREATED

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        taxi = self.get_object(pk)

        try:
            order = PassengerOrder.objects.get(taxi_id=taxi.id)
            order.remove_taxi()
        except PassengerOrder.DoesNotExist:
            pass

        taxi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PassengerOrderAPI(APIView):
    """
    API for the passengers: for calling a taxi or to cancel their orders
    """

    parser_classes = (FormParser, JSONParser,)

    @staticmethod
    def get_object(pk, rise_exception=True):
        try:
            return PassengerOrder.objects.get(passenger_id=pk)
        except PassengerOrder.DoesNotExist:
            if rise_exception:
                raise Http404
            else:
                return False

    def get(self, request, pk, format=None):
        order = self.get_object(pk)
        serializer = PassengerOrderSerializer(order)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        data = request.data.dict() if isinstance(request.data, QueryDict) else request.data
        data['passenger_id'] = pk
        err = False

        order = self.get_object(pk, rise_exception=False)
        if order:
            serializer = PassengerOrderSerializer(order, data=data)

            # can't change location in case of awaiting for the taxi
            if order.is_waiting_for_taxi():
                err = True
                st = status.HTTP_403_FORBIDDEN
            else:
                st = status.HTTP_200_OK
        else:
            serializer = PassengerOrderSerializer(data=data)
            serializer.key = pk
            st = status.HTTP_201_CREATED

        if err:
            return Response(serializer.data, status=st)
        elif serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        order = self.get_object(pk)

        taxi = TaxiLocation.get_object(order.taxi_id, rise_exception=False)
        if taxi:
            taxi.change_activity(is_busy=False)

        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
