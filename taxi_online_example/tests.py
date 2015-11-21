# -*- coding: utf-8 -*-

import time
import logging
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from taxi_online_example.models import TaxiLocation, PassengerOrder
from taxi_online_example.service import process_passengers


class BaseRestTestCase(TestCase):

    def setUp(self):
        # Don't show logging messages while testing
        logging.disable(logging.CRITICAL)

        TaxiLocation.objects.all().delete()
        PassengerOrder.objects.all().delete()

    def test_taxi_location_api(self):
        taxi_id = 1
        client = APIClient()

        # test create
        response = client.post('/taxi/%d/location/' % taxi_id, {'lat': 12.01, 'lon': 76.000123}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'lat': '12.010000', 'lon': '76.000123', "taxi_id": str(taxi_id)})
        self.assertEqual(TaxiLocation.objects.count(), 1)

        # check that there are no more than 6 decimal places in lat and lon params
        response = client.post('/taxi/%d/location/' % taxi_id, {'lat': 12.1234567, 'lon': 76.1234567}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to add invalid lat and lon
        response = client.post('/taxi/%d/location/' % taxi_id, {'lat': -91, 'lon': 180}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to add invalid lat and lon
        response = client.post('/taxi/%d/location/' % taxi_id, {'lat': -89, 'lon': 181}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test update
        response = client.post('/taxi/%d/location/' % taxi_id, {'lat': 12.02, 'lon': 76.000124}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'lat': '12.020000', 'lon': '76.000124', "taxi_id": str(taxi_id)})
        self.assertEqual(TaxiLocation.objects.count(), 1)

        # test get
        response = client.get('/taxi/%d/location/' % taxi_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'lat': '12.020000', 'lon': '76.000124', "taxi_id": str(taxi_id)})

        # test delete
        response = client.delete('/taxi/%d/location/' % taxi_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaxiLocation.objects.count(), 0)

    def test_passenger_order_api(self):
        passenger_id = 'test_id'
        passenger_id2 = 'test_id2'
        client = APIClient()

        # test create
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 1.01, 'lon': 2.002}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'lat': '1.010000','lon': '2.002000', "passenger_id": str(passenger_id),
                                         'time_to_pick_up': response.data['time_to_pick_up']})
        self.assertEqual(PassengerOrder.objects.count(), 1)

        # check that there are no more than 6 decimal places in lat and lon params
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 1.1234567, 'lon': 2.1234567},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to add invalid lat and lon
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': -91, 'lon': 180}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # try to add invalid lat and lon
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': -89, 'lon': 181}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # check that time_to_pick_up couldn't be in the past
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 1.123, 'lon': 2.123,
                                                                       'time_to_pick_up': int(time.time()) - 1},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # test create order with time_to_pick_up in future
        t1 = int(time.time()) + 100
        response = client.post('/passenger/%s/order/' % passenger_id2, {'lat': 1.01, 'lon': 2.002,
                                                                        'time_to_pick_up': t1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'lat': '1.010000','lon': '2.002000', "passenger_id": str(passenger_id2),
                                         'time_to_pick_up': t1})
        self.assertEqual(PassengerOrder.objects.count(), 2)

        # test update
        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 12.02, 'lon': 76.000124}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'lat': '12.020000','lon': '76.000124', "passenger_id": str(passenger_id),
                                         'time_to_pick_up': response.data['time_to_pick_up']})
        self.assertEqual(PassengerOrder.objects.count(), 2)

        # test get
        response = client.get('/passenger/%s/order/' % passenger_id2, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'lat': '1.010000','lon': '2.002000', "passenger_id": str(passenger_id2),
                                         'time_to_pick_up': t1})

        # test delete
        response = client.delete('/passenger/%s/order/' % passenger_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PassengerOrder.objects.count(), 1)

    def test_processing(self):
        taxi_id1 = 1
        taxi_id2 = 2
        passenger_id = 1
        client = APIClient()

        response = client.post('/taxi/%d/location/' % taxi_id1, {'lat': 56.312719, 'lon': 43.845431}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post('/taxi/%d/location/' % taxi_id2, {'lat': 55.312719, 'lon': 41.845431}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(TaxiLocation.objects.count(), 2)

        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 56.315855, "lon": 44.003525},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PassengerOrder.objects.count(), 1)

        process_passengers()

        order = PassengerOrder.objects.get(passenger_id=passenger_id)
        self.assertEqual(int(order.taxi_id), taxi_id1)
        taxi = TaxiLocation.objects.get(taxi_id=taxi_id1)
        self.assertTrue(taxi.is_busy)

        # test delete
        response = client.delete('/passenger/%s/order/' % passenger_id, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PassengerOrder.objects.count(), 0)
        taxi = TaxiLocation.objects.get(taxi_id=taxi_id1)
        self.assertFalse(taxi.is_busy)

    def test_processing_taxi_is_too_far(self):
        taxi_id1 = 1
        taxi_id2 = 2
        passenger_id = 1
        client = APIClient()

        response = client.post('/taxi/%d/location/' % taxi_id1, {'lat': 34.312719, 'lon': 68.845431}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = client.post('/taxi/%d/location/' % taxi_id2, {'lat': 33.312719, 'lon': 69.845431}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(TaxiLocation.objects.count(), 2)

        response = client.post('/passenger/%s/order/' % passenger_id, {'lat': 56.315855, "lon": 44.003525},
                               format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PassengerOrder.objects.count(), 1)

        process_passengers()

        order = PassengerOrder.objects.get(passenger_id=passenger_id)
        self.assertEqual(order.taxi_id, None)