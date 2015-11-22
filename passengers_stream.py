#!/usr/bin/env python

import time
import random
import requests

server_name = 'ec2-52-18-8-159.eu-west-1.compute.amazonaws.com'
timeout = 3

while True:
    lon = "%.6f" % random.uniform(-180.000000, 180.000000)
    lat = "%.6f" % random.uniform(-90.000000, 90.000000)
    passenger_id = random.randint(1, 10000000)
    post_data = {"lon": str(lon), "lat": str(lat)}

    res = random.choice([0, 1])
    if res:
        post_data['time_to_pick_up'] = int(time.time()) + random.randint(60, 300)

    r = requests.post("http://%s/passenger/%s/order/" % (server_name, str(passenger_id)), data=post_data)
    print r.status_code, r.reason, r.text
    time.sleep(timeout)


