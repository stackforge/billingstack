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

.. _subscription:


============
Subscription
============

.. index::
    double: subscription; brief

Process
+++++++

.. note:: Try to outline a sample subscription creation process.

* Prerequisites: Registered Merchant with API credentials configured for a Service.

1. The :term:`merchant` configures a API access key for others services.
2. Have an external service to create a new subscription against
    BillingStack when a new :term:`resource` is created in a system.

3. Subscription is either created towards an existing :term:`customer` or
    if the :term:`merchant` has a setting configured to allow :term:`customer`
    created if the given :term:`customer` doesn't exist it will be created along with
    subscription.
4. When a subscription is created we're ready to receive events from a system.