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

.. _payments:


=====================
Payments Architecture
=====================

.. index::
    double: payments; brief


Payment Gateway
+++++++++++++++

A PaymentGateway is a service running on the outside of BS. It's typically
something like Braintree, PayPal, eNets, DIBS, Authorize or any other service
that you want to use.

Inside of BillingStack:
BillingStack refers to a implementation of a PaymentGateway as a PGP which is a
plugin that provides a set of methods that BillingStack needs in order to do
it's operations towards the PaymentGateway service.


Payment Gateway Provider
++++++++++++++++++++++++

The Payment Gateway Provider (PGP) module is installed standalone of the
core service. This is done to not having to install whatever dependencies
the underlying modules the libraries it builds on needs if you only need a
specific provider.

A PGP is "registered" into the database after installing it.
See :doc:`pgp` for information on this.

Reasoning behind PGP architecture:

* Systems that doesn't have the PGP modules installed won't know about PGP
  information without this.

* Implementation of a in-house system becomes very easy, write a new PGP that
  does what you need, install, register and you are good to go. BS doesn't care
  on what technology you use.


Payment Gateway Method
++++++++++++++++++++++

The PGM is just a string or something to tell what methods are supported by
the PGP. Like 'visa' or any other string, piece of data or similar.


Payment Gateway Configuration
+++++++++++++++++++++++++++++

A Payment Gateway Configuration refers to either a piece of configuration stored
in the database or a configuration section in a config file (Useful for things
that shouldn't be stored in the DB because of law or similar).
