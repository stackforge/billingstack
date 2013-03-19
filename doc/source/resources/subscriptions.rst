..
    Copyright 2013 Endre Karlson <endre.karlson@gmail.com>
    Copyright 2013 Luis Gervaso <luis@woorea.es>

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

Prerequisites
+++++++++++++

.. note:: BillingStack does not store merchant customer users. Merchant should manage authorization.

1. Merchant and Plan created in BillingStack

2. bs-admin Role create in Merchant Identity Manager (e.g keystone)

Process
+++++++

.. note:: Try to outline a sample subscription creation process.

1. User registers in the merchant portal application using the merchant identity manager (e.g keystone)

  POST /v2.0/users

2. User login in the merchant portal application using merchant identity manager (e.g keystone)

  POST /v2.0/tokens

  At this point user has an unscoped token

3. User decides to subscribe in one of the merchant plans

  3.1 Using the merchan API key & secret portal gathers all the available plans from BillingStack
    
    GET /merchants/<merchant_id>/plans

  3.2 User select the desired plan to subscribe in

    3.1 Since the current token is unscoped it's necessary to create customer in BillingStack

        POST /merchant/<merchant_id>/customers

        Using the customer_id obtained from BillingStack a new OpenStack tenant is created
        this special tenant should be named as : bs-customer-<customer_id>

        POST /v2.0/tenants

        PUT /v2.0/tenants/<tenant_id>/users/<user_id>/role/<openstack_admin_role_id>
        PUT /v2.0/tenants/<tenant_id>/users/<user_id>/role/<billingstack_admin_role_id>

        Now it is necessary exchange the unscoped token to a scoped one

        POST /v2.0/tokens

    3.2 BillingStack subscription is created for the BillingStack customer

        3.2.1 Create the BillingStack Subscription

          POST /merchants/<merchant_id>/subscriptions

        3.2.2 Create a new OpenStack tenant

          POST /tenants

          This tenant should be named bs-subscription-<subscription_id>

        3.2.3 Add OpenStack user to the recently created tenant

          PUT /tenants/<tenant_id>/users/<user_id>/roles/<openstack_admin_role_id>

        3.2.4 Update subscription resource attribute with the tenant id from OpenStack

        PATCH /merchants/<merchant_id>/subscriptions/<subscription_id>

4. Now the subscription can start receiving usage data from ceilometer tied by resource attribute
