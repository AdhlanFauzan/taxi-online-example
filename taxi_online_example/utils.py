# -*- coding: utf-8 -*-

import time
import datetime
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.decorators import decorator_from_middleware
from taxi_online_example.middleware import RequestLogMiddleware


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return datetime.timedelta(0)


class UnixEpochDateField(serializers.DateTimeField):
    def to_representation(self, value):
        """ Return epoch time for a datetime object or ``None``"""
        try:
            return int(time.mktime(value.timetuple()))
        except (AttributeError, TypeError):
            return None

    def to_internal_value(self, value):
        try:
            return datetime.datetime.fromtimestamp(int(value), tz=UTC())
        except ValueError:
            return value


class RequestLogViewMixin(object):
    """
    Adds RequestLogMiddleware to any Django View by overriding as_view.
    """

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(RequestLogViewMixin, cls).as_view(*args, **kwargs)
        view = decorator_from_middleware(RequestLogMiddleware)(view)
        return view


def date_now_or_future_validator(value):
    if not isinstance(value, (datetime.datetime, int)):
        try:
            int(value)
        except ValueError:
            raise ValidationError('Incorrect format of date. It should be a unixtimestamp')

    if value < datetime.datetime.now(tz=UTC()):
        raise ValidationError('Date and time shouldn\'t be less then the current')