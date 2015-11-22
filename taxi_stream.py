#!/usr/bin/env python

import time
import random
import requests

server_name = 'example.com'
timeout = 3

while True:
    lon = "%.6f" % random.uniform(-180.000000, 180.000000)
    lat = "%.6f" % random.uniform(-90.000000, 90.000000)
    taxi_id = random.randint(1, 10000000)

    r = requests.post("http://%s/taxi/%s/location/" % (server_name, str(taxi_id)),
                      data={"lon": str(lon), "lat": str(lat)})
    print r.status_code, r.reason, r.text
    time.sleep(timeout)


