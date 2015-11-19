from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from taxi_online_example.models import TaxiLocation, PassengerOrder
from taxi_online_example.serializers import TaxiLocationSerializer, PassengerOrderSerializer


class TaxiLocationAPI(APIView):
    """
    API for the taxi drivers: for sending to server information about current location and availability to pick up some passengers
    """

    def get_object(self, pk):
        try:
            return TaxiLocation.objects.get(taxi_id=pk)
        except TaxiLocation.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        taxi = self.get_object(pk)
        serializer = TaxiLocationSerializer(taxi)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        data = request.data.dict()
        data['taxi_id'] = pk

        try:
            taxi = self.get_object(pk)
            serializer = TaxiLocationSerializer(taxi, data=data)
            st = status.HTTP_201_CREATED
        except Http404:
            serializer = TaxiLocationSerializer(data=data)
            serializer.key = pk
            st = status.HTTP_200_OK

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        taxi = self.get_object(pk)
        taxi.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PassengerOrderAPI(APIView):
    """
    API for the passengers: for calling a taxi or to cancel their orders
    """

    def get_object(self, pk):
        try:
            return PassengerOrder.objects.get(passenger_id=pk)
        except PassengerOrder.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        passenger = self.get_object(pk)
        serializer = PassengerOrderSerializer(passenger)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        data = request.data.dict()
        data['passenger_id'] = pk

        try:
            passenger = self.get_object(pk)
            serializer = PassengerOrderSerializer(passenger, data=data)
            st = status.HTTP_201_CREATED
        except Http404:
            serializer = PassengerOrderSerializer(data=data)
            serializer.key = pk
            st = status.HTTP_200_OK

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        passenger = self.get_object(pk)
        passenger.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

