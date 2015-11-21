# -*- coding: utf-8 -*-

import logging
import uuid
from django.db import IntegrityError, transaction
from taxi_online_example.models import PassengerOrder

logger = logging.getLogger('processing')


def process_passengers():
    orders = PassengerOrder.get_all_passengers_for_pick_up()

    for order in orders:
        identifier = str(uuid.uuid4())

        _log(identifier, 'Try to process order', order.description())

        taxi = order.get_nearest_free_taxi()
        if taxi:
            _log(identifier, 'The nearest taxi is: ', taxi.description())
            try:
                with transaction.atomic():
                    order.taxi_id = taxi.taxi_id
                    order.save()
                    taxi.is_busy = True
                    taxi.save()
                    _log(identifier, 'The taxi was successfully assigned!')
            except IntegrityError:
                # in case of race condition this taxi became busy
                # and database will rise an unique exception on field PassengerOrder.taxi_id
                # don't do anything - this passenger will be processed on the next iteration
                _log(identifier, 'Something wrong! The taxi wasn\'t assigned!')
        else:
            _log(identifier, 'Can\'t find the taxi')


def _log(identifier, *msgs):
    logger.info(' '.join(msgs), extra={'identifier': identifier})