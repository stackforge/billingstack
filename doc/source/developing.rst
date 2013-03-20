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

.. _developing:

=======================
Developing BillingStack
=======================


Setting up a development environment
====================================

.. index::
    double: development; env

There are 2 ways to setting up a development environment
* :doc:install/manual - Manual setup for a more distributed / semi production env
* This: :ref:`development-env`

1. Clone the repo - see :ref:`cloning-git` for generic information::

    $ git clone http://github.com/billingstack/billingstack

2. Change directory to the BS directory::

    $ cd billingstack

3. Setup a virtualenv with all deps included for the core::

    $ python tools/install_venv.py

Now wait for it to be ready ( Take a coffe break? )

3. Active the virtualenv::

    $ source .venv/bin/activate

4. You're ready to have fun!


Running tests
=============

Using tox you can test towards multiple different isolated environments.

For example if you want to test your PEP8 coverage that is needed to pass for
a change to merge::

    $ tox -e pep8

Running the actualy in Python 2.7 tests::

    $ tox -e py27 -v -- -v