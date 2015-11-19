from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from taxi_online_example.models import Taxi, Passenger
from taxi_online_example.serializers import TaxiSerializer, PassengerSerializer


class TaxiDetail(APIView):

    def get_object(self, pk):
        try:
            return Taxi.objects.get(key=pk)
        except Taxi.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        taxi = self.get_object(pk)
        serializer = TaxiSerializer(taxi)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        try:
            taxi = self.get_object(pk)
            serializer = TaxiSerializer(taxi, data=request.data)
            st = status.HTTP_201_CREATED
        except Http404:
            serializer = TaxiSerializer(data=request.data)
            serializer.key = pk
            st = status.HTTP_200_OK

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PassengerDetail(APIView):

    def get_object(self, pk):
        try:
            return Passenger.objects.get(key=pk)
        except Passenger.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        taxi = self.get_object(pk)
        serializer = PassengerSerializer(taxi)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        try:
            taxi = self.get_object(pk)
            serializer = PassengerSerializer(taxi, data=request.data)
            st = status.HTTP_201_CREATED
        except Http404:
            serializer = PassengerSerializer(data=request.data)
            serializer.key = pk
            st = status.HTTP_200_OK

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=st)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

