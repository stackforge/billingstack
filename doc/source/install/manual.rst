..
      Copyright 2013 Endre Karlson <endre.karlson@gmail.com>

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.



=====================
 Installing Manually
=====================

Common Steps
============

.. index::
   double: installing; common_steps

.. note::
   The below operations should take place underneath your <project>/etc folder.

1. Install system package dependencies (Ubuntu)

  ::

    $ apt-get install python-pip
    $ apt-get install rabbitmq-server

2. Clone the BillingStack repo off of Github

  ::

    $ git clone https://github.com/billingstack/billingstack.git
    $ cd billingstack

3. Setup virtualenv and Install BillingStack and it's dependencies

  .. note::

      This is to not interfere with system packages etc.
  ::

    $ pip install virtualenv
    $ python tools/install_venv.py
    $ . .venv/bin/activate
    $ python setup.py develop


  Copy sample configs to usable ones, inside the `etc` folder do

  ::

    $ sudo cp -r etc/billingstack /etc
    $ cd /etc/billingstack
    $ sudo ls *.sample | while read f; do cp $f $(echo $f | sed "s/.sample$//g"); done

  .. note::

    Change the wanted configuration settings to match your environment, the file
    is in the `/etc/billingstack` folder

  ::

    $ vi /etc/billingstack/billingstack.conf


Installing Central
==================

.. index::
   double: installing; central

.. note::
   This is needed because it is the service that the API and others uses to
   communicate with to do stuff in the Database.

1. See `Common Steps`_ before proceeding.

2. Create the DB for :term:`central`

  ::

    $ python tools/resync_billingstack.py

3. Now you might want to load sample data for the time being

  ::

    $ python tools/load_samples.py

4. Start the central service

  ::

    $ billingstack-central

    ...

    2013-06-09 03:51:22    DEBUG [amqp] Open OK!
    2013-06-09 03:51:22    DEBUG [amqp] using channel_id: 1
    2013-06-09 03:51:22    DEBUG [amqp] Channel open
    2013-06-09 03:51:22     INFO [...] Connected to AMQP server on localhost:5672
    2013-06-09 03:51:22    DEBUG [...] Creating Consumer connection for Service central


Installing the API
====================

.. index::
   double: installing; api

.. note::
   The API Server needs to able to talk via MQ to other services.

1. See `Common Steps`_ before proceeding.

2. Start the API service

  ::

    $ billingstack-api

    ...

    2013-06-09 03:52:31     INFO [eventlet.wsgi] (2223) wsgi starting up on http://0.0.0.0:9091/