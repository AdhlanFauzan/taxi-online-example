# -*- coding: utf-8 -*-

import time
import logging
from django.core.management.base import BaseCommand
from taxi_online_example.service import process_passengers


logger = logging.getLogger('processing')


class Command(BaseCommand):

    help = u'Process current orders (for usage as a CRON task)'
    default_times_to_repeat = 1
    default_timeout = 5

    def add_arguments(self, parser):
        parser.add_argument('--times_to_repeat',
                            action='store',
                            dest='times_to_repeat',
                            default=self.default_times_to_repeat,
                            help='how many times to repeat the process of getting orders for database')
        parser.add_argument('--timeout_before_repeat',
                            action='store',
                            dest='timeout_before_repeat',
                            default=self.default_timeout,
                            help='timeout in seconds before repeat the search for the waiting passengers')

    def handle(self, *args, **options):
        times_to_repeat = self.default_times_to_repeat
        if options['times_to_repeat']:
            times_to_repeat = int(options['times_to_repeat'])

        timeout_before_repeat = self.default_timeout
        if options['timeout_before_repeat']:
            timeout_before_repeat = int(options['timeout_before_repeat'])

        for i in xrange(times_to_repeat):
            print 'Attempt num ', str(i+1), ':'
            print ''
            process_passengers()
            print ''

            if (i+1) != times_to_repeat:
                time.sleep(timeout_before_repeat)