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

Process
+++++++

.. note:: Try to outline a sample subscription creation process.



* Prerequisites: Registered Merchant with API credentials configured and a merchant plan available.

1. User registers in the merchant portal application using the merchant identity manager (e.g keystone)

2. Portal gathers the available plans from BillingStack
    
    GET /merchants/<merchant_id>/plans

3. User select the desired plan to subscribe in

    3.1 If user is not registered in BillingStack then portal will register first the user in BillingStack
        for a customer account

        POST /users

        POST /accounts

        PUT /account/<account_id>/users/<user_id>/roles/<customer_admin_role_id>

        PUT /merchants/<merchant_id>/customers/<account_id>

        At this point the user is registered in BillingStack

    3.2 BillingStack subscription is created for the BillingStack customer

        3.1 Create the BillingStack Subscription

        POST /merchants/<merchant_id>/subscriptions

        3.2 Create a new OpenStack tenant

        POST /tenants

        3.3 Add OpenStack user to the recently created tenant

        PUT /tenants/<tenant_id>/users/<openstack_user_id>/roles/<openstack_admin_role_id>

        3.4 Update subscription resource attribute with the tenant id from OpenStack

        PATCH /merchants/<merchant_id>/subscriptions/<subscription_id>
4. Now the subscription can start receiving usage data from ceilometer tied by resource attribute