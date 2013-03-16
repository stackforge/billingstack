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

1. Install system package dependencies (Ubuntu)::

   $ apt-get install python-pip python-virtualenv
   $ apt-get install rabbitmq-server mysql-server
   $ apt-get build-dep python-lxml

2. Clone the BillingStack repo off of Github::

   $ git clone https://github.com/billingstack/billingstack.git
   $ cd billingstack

3. Setup virtualenv::

.. note::
   This is to not interfere with system packages etc.

   $ virtualenv --no-site-packages .venv
   $ . .venv/bin/activate

4. Install BillingStack and it's dependencies::

   $ pip install -rtools/setup-requires -rtools/pip-requires -rtools/pip-options
   $ python setup.py develop

   Copy sample configs to usable ones, inside the `etc` folder do::

   $ ls *.sample | while read f; do cp $f $(echo $f | sed "s/.sample$//g"); done


Installing Central
==================

.. index::
   double: installing; central

.. note::
   This is needed because it is the service that the API and others uses to
   communicate with to do stuff in the Database.

1. See `Common Steps`_ before proceeding.

2. Configure the :term:`central` service::

   Change the wanted configuration settings to match your environment, the file
   is in the `etc` folder::

   $ vi etc/billingstack.conf

   Refer to the configuration file for  details on configuring the service.

3. Create the DB for :term:`central`::

   $ python tools/resync_billingstack.py

4. Now you might want to load sample data for the time being::

   $ python tools/dev_samples.py

5. Start the central service::

   $ billingstack-central


Installing a PGP
================

.. index:
   double: installing; pgp

.. note::
   This is REQUIRED to be installed on the same machine that has access to
   the database and that has the billingstack-manage command.

1. Clone a provider repo off of github::

   $ git clone git@github.com:billingstack/billingstack-braintree.git

2. Install it in the SAME env / venv as the main billingstack package::

   $ pip install -rtools/setup-requires -rtools/pip-requires -rtools/pip-options
   $ python setup.py develop

3. Now register :term:`pgp` with it's :term:`pgm`::

   $ billingstack-manage pg-register


Installing the API
====================

.. index::
   double: installing; api

.. note::
   The API Server needs to able to talk via MQ to other services.

1. See `Common Steps`_ before proceeding.

2. Configure the :term:`api` service::

   Change the wanted configuration settings to match your environment, the file
   is in the `etc` folder::

   $ vi billingstack.conf

   Refer to the configuration file for  details on configuring the service.

3. Start the API service::

   $ billingstack-api