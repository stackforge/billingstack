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

.. _architecture:


============
Glossary
============

.. glossary::
    pgp
        PaymentGatewayProvider - A plugin for PaymentGateways
    pgm
        PaymentGatewayMethod - A supported payment method by the PGP
    api
        Web API
    central
        The Central service that does CRUD operations and more in BS.
    customer
        An entity underneath :term:`merchant` that holds different data that
        resembles a Customer in an external system like a Tenant, Project etc.
    merchant
        An entity that holds one or more users, can configure integration with
        third party services like OpenStack ceilometer, configure api
        credentials for API access etc.