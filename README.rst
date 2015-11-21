Requirements
============

* Python 2.6 or 2.7
* virtualenv + pip
* PostgreSQL server

Installation
============

At first you should install PostgreSQL (probably it will work on MySQL but I'm not sure).

The recommended way of deploying the current project is to use virtualenv:

.. code-block:: bash

  mkdir venv && echo "Virtualenv directory" > venv/README
  virtualenv --no-site-packages --prompt="(taxi_online_example)" venv
  source venv/bin/activate
  pip install -r requirements.txt

After you have created virtualenv directory you should create *settings.py* file to implement your own enviroment settings (at least you should change settings for connection to PostgreSQL):

.. code-block:: bash

  cd taxi_online_example
  cp settings.example.py settings.py
  vim settings.py

Also you need to create empty database and user for the project:

.. code-block:: sql

  CREATE DATABASE test_taxi_online_example;
  CREATE USER taxi WITH password 'taxi';
  ALTER USER taxi CREATEDB;
  GRANT ALL privileges ON DATABASE test_taxi_online_example TO taxi;

After DB preparation will be finished you need to create empty DB structure:

.. code-block:: bash

  source venv/bin/activate
  python manage.py syncdb

To run the process of processing orders you need to execute the command:

.. code-block:: bash

  source venv/bin/activate
  python manage.py process_orders

So in production enviroment you should add in crontab the below string:

.. code-block:: bash

  * * * * * source venv/bin/activate; python manage.py process_orders --times_to_repeat=5

How to run default Django web server
====================================

.. code-block:: bash

  source venv/bin/activate
  python manage.py runserver 0.0.0.0:8000


How to run unit tests
=====================

.. code-block:: bash

  source venv/bin/activate
  python manage.py test --keepdb -v 2

Logging
=======

All logs you could find here:

.. code-block:: bash

  <project_path>/logs/django.api.requests.log
  <project_path>/logs/django.requests.log
  <project_path>/logs/processing.log

REST API
========

.. code-block:: bash

  # to get information about the location of the taxi with ID 123
  curl "http://0.0.0.0:8000/taxi/123/location/" -v

  # to create or update the location of taxi with ID 123
  curl --data "lat=56.312719&lon=43.845431" "http://0.0.0.0:8000/taxi/123/location/" -v

  # to remove the location of taxi with ID 123 (the driver goes to sleep)
  curl -X DELETE "http://0.0.0.0:8000/taxi/123/location/" -v

  # to get information about the order for the passenger with ID 456
  curl "http://0.0.0.0:8000/passenger/456/order/" -v

  # to create or update new order that the passenger with ID 456 will be picked up just now
  curl --data "lat=56.312719&lon=43.845431" "http://0.0.0.0:8000/passenger/456/order/" -v

  # to create or update new order that the passenger with ID 456 will be picked up sometimes in future
  # (unixtimestamp as a param)
  curl --data "lat=56.312719&lon=43.845431&time_to_pick_up=1448577995" "http://0.0.0.0:8000/passenger/456/order/" -v

  # to remove the order for the passenger with ID 456
  curl -X DELETE "http://0.0.0.0:8000/passenger/456/order/" -v
