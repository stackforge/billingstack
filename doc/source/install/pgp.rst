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


Installing a PGP
================

.. index:
   double: installing; pgp

.. note::
   This is REQUIRED to be installed on the same machine that has access to
   the database and that has the billingstack-manage command.

.. note::
    A PGP Can be installed either inside a virtualenv where the bs core is
    installed or in a system wide install.


Python modules
==============

1. Clone a provider repo off of github::

   $ git clone git@github.com:billingstack/billingstack-braintree.git

2. Install it in the SAME environment / virtualenv as the main billingstack core::

   $ pip install -rtools/setup-requires -rtools/pip-requires -rtools/pip-options
   $ python setup.py develop


Registering the PGP
===================

.. note::
    So while the module is actually installed Python wise, it's needed to
    load up some data into the database so the system knows of its existance.

1. Install the PGP module using the process described above.

2. Register :term:`pgp` with it's :term:`pgm`::

   $ billingstack-manage pg-register

3. Check the logs that the utility gives and list out registered pgp's::

    $ billingstack-manage pg-list

