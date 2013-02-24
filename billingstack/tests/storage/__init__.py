# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# Copied: Moniker
from billingstack.openstack.common import log as logging
from billingstack.storage.impl_sqlalchemy import models
from billingstack.tests.base import TestCase


LOG = logging.getLogger(__name__)


UUID = 'caf771fc-6b05-4891-bee1-c2a48621f57b'


class StorageDriverTestCase(TestCase):
    __test__ = False

    # Currencies
    def test_currency_add(self):
        self.assertDuplicate(self.currency_add)

    # Languages
    def test_language_add(self):
        self.assertDuplicate(self.language_add)

    # Payment Gateways
    def test_pg_provider_register(self):
        fixture, actual = self.pg_provider_register()
        self.assertEqual(fixture['name'], actual['name'])
        self.assertEqual(fixture['title'], actual['title'])
        self.assertEqual(fixture['description'], actual['description'])
        self.assertData(fixture['methods'][0], actual['methods'][0])

    def test_pg_provider_register_different_methods(self):
        # Add a Global method
        method1 = {'type': 'creditcard', 'name': 'mastercard'}
        self.storage_conn.pg_method_add(method1)

        method2 = {'type': 'creditcard', 'name': 'amex'}
        self.storage_conn.pg_method_add(method2)

        method3 = {'type': 'creditcard', 'name': 'visa', 'owned': 1}

        methods = [method1, method2, method3]
        provider = {'name': 'noop'}

        provider = self.storage_conn.pg_provider_register(provider, methods)

        # TODO(ekarls): Make this more extensive?
        self.assertLen(3, provider['methods'])

    def test_pg_provider_register_method_switch_methods(self):
        provider_data = {'name': 'noop'}

        system_method = {
            'type': 'creditcard',
            'name': 'mastercard',
            'title': "random"}
        self.storage_conn.pg_method_add(system_method)

        provider = self.storage_conn.pg_provider_register(
            provider_data,
            [system_method])
        self.assertLen(1, provider['methods'])
        self.assertData(system_method, provider['methods'][0])

        provider_method = {
            'type': 'creditcard',
            'name': 'mastercard',
            'title': 'random2',
            'owned': 1}

        provider = self.storage_conn.pg_provider_register(
            provider_data,
            [provider_method])
        self.assertLen(1, provider['methods'])
        self.assertData(provider_method, provider['methods'][0])

        provider = self.storage_conn.pg_provider_register(
            provider_data,
            [system_method])
        self.assertLen(1, provider['methods'])
        self.assertData(system_method, provider['methods'][0])

    def test_pg_provider_get(self):
        _, expected = self.pg_provider_register()
        actual = self.storage_conn.pg_provider_get(expected['id'])
        self.assertData(expected, actual)

    def test_pg_provider_get_missing(self):
        self.assertMissing(self.storage_conn.pg_provider_get, UUID)

    def test_pg_provider_deregister(self):
        _, data = self.pg_provider_register()
        self.storage_conn.pg_provider_deregister(data['id'])
        self.assertMissing(self.storage_conn.pg_provider_deregister, data['id'])

    def test_pg_provider_deregister_missing(self):
        self.assertMissing(self.storage_conn.pg_provider_deregister, UUID)

    # Payment Gateway Configuration
    def test_pg_config_add(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])
        self.assertData(fixture, data)

    def test_pg_config_get(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

    def test_pg_config_get_missing(self):
        self.assertMissing(self.storage_conn.pg_config_get, UUID)

    def test_pg_config_update(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        fixture['configuration'] = {"api": 1}
        updated = self.storage_conn.pg_config_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_pg_config_update_missing(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.assertMissing(self.storage_conn.pg_config_update, UUID, {})

    def test_pg_config_delete(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.storage_conn.pg_config_delete(data['id'])
        self.assertMissing(self.storage_conn.pg_config_get, data['id'])

    def test_pg_config_delete_missing(self):
        self.assertMissing(self.storage_conn.pg_config_delete, UUID)

    # PaymentMethod
    def test_payment_method_add(self):
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']
        _, customer = self.customer_add(self.merchant['id'])

        fixture, data = self.payment_method_add(customer['id'], m_id)
        self.assertData(fixture, data)

    def test_payment_method_get(self):
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']
        _, customer = self.customer_add(self.merchant['id'])

        _, expected = self.payment_method_add(customer['id'], m_id)
        actual = self.storage_conn.payment_method_get(expected['id'])
        self.assertData(expected, actual)

    # TODO(ekarlso): Make this test more extensive?
    def test_payment_method_list(self):
        # Setup a PGP with it's sample methods
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']

        # Add two Customers with some methods
        _, customer1 = self.customer_add(self.merchant['id'])
        self.payment_method_add(customer1['id'], m_id)
        rows = self.storage_conn.payment_method_list(customer1['id'])
        self.assertLen(1, rows)

        _, customer2 = self.customer_add(self.merchant['id'])
        self.payment_method_add(customer2['id'], m_id)
        self.payment_method_add(customer2['id'], m_id)
        self.assertLen(2, self.storage_conn.payment_method_list(customer2['id']))

    def test_payment_method_get_missing(self):
        self.assertMissing(self.storage_conn.payment_method_get, UUID)

    def test_payment_method_update(self):
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']
        _, customer = self.customer_add(self.merchant['id'])

        fixture, data = self.payment_method_add(customer['id'], m_id)

        fixture['identifier'] = 1
        updated = self.storage_conn.payment_method_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_payment_method_update_missing(self):
        self.assertMissing(self.storage_conn.payment_method_update, UUID, {})

    def test_payment_method_delete(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.storage_conn.pg_config_delete(data['id'])
        self.assertMissing(self.storage_conn.payment_method_delete, data['id'])

    def test_payment_method_delete_missing(self):
        self.assertMissing(self.storage_conn.payment_method_delete, UUID)

    # Merchant
    def test_merchant_add(self):
        fixture, data = self.merchant_add()
        self.assertData(fixture, data)

    def test_merchant_get(self):
        _, expected = self.merchant_add()
        actual = self.storage_conn.merchant_get(expected['id'])
        self.assertData(expected, actual)

    def test_merchant_get_missing(self):
        self.assertMissing(self.storage_conn.merchant_get, UUID)

    def test_merchant_update(self):
        fixture, data = self.merchant_add()

        fixture['name'] = 'test'
        updated = self.storage_conn.merchant_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_merchant_update_missing(self):
        self.assertMissing(self.storage_conn.merchant_update, UUID, {})

    def test_merchant_delete(self):
        self.storage_conn.merchant_delete(self.merchant['id'])
        self.assertMissing(self.storage_conn.merchant_get, self.merchant['id'])

    def test_merchant_delete_missing(self):
        self.assertMissing(self.storage_conn.merchant_delete, UUID)

    # Customer
    def test_customer_add(self):
        fixture, data = self.customer_add(self.merchant['id'])
        assert data['default_info'] == None
        self.assertData(fixture, data)

    def test_customer_add_with_contact_info(self):
        contact_fixture = self.get_fixture('contact_info')
        customer_fixture, data = self.customer_add(
            self.merchant['id'],
            contact_info=contact_fixture)
        self.assertData(customer_fixture, data)
        self.assertData(contact_fixture, data['default_info'])

    def test_customer_get(self):
        _, expected = self.customer_add(self.merchant['id'])
        actual = self.storage_conn.customer_get(expected['id'])
        self.assertData(expected, actual)

    def test_customer_get_missing(self):
        self.assertMissing(self.storage_conn.customer_get, UUID)

    def test_customer_update(self):
        fixture, data = self.customer_add(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.customer_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_customer_update_missing(self):
        self.assertMissing(self.storage_conn.customer_update, UUID, {})

    def test_customer_delete(self):
        _, data = self.customer_add(self.merchant['id'])
        self.storage_conn.customer_delete(data['id'])
        self.assertMissing(self.storage_conn.customer_get, data['id'])

    def test_customer_delete_missing(self):
        self.assertMissing(self.storage_conn.customer_delete, UUID)

    # User
    def test_user_add(self):
        fixture, data = self.user_add(self.merchant['id'])
        assert data['contact_info'] == None
        self.assertData(fixture, data)

    def test_user_add_with_contact_info(self):
        contact_fixture = self.get_fixture('contact_info')
        user_fixture, data = self.user_add(
            self.merchant['id'],
            contact_info=contact_fixture)
        self.assertData(user_fixture, data)
        self.assertData(contact_fixture, data['contact_info'])

    def test_user_add_with_customer(self):
        _, customer = self.customer_add(self.merchant['id'])
        fixture, data = self.user_add(self.merchant['id'], customer_id=customer['id'])
        self.assertData(fixture, data)

    def test_user_list(self):
        self.assertLen(0, self.storage_conn.user_list(self.merchant['id']))

        self.user_add(self.merchant['id'])
        rows = self.storage_conn.user_list(self.merchant['id'])
        self.assertLen(1, rows)

    def test_user_list_customer(self):
        self.assertLen(0, self.storage_conn.user_list(self.merchant['id']))

        # NOTE: Add 1 user for the Merchant and 1 with a Customer
        _, merchant_user = self.user_add(self.merchant['id'])

        _, customer = self.customer_add(self.merchant['id'])
        _, customer_user = self.user_add(self.merchant['id'], customer_id=customer['id'])

        rows = self.storage_conn.user_list(self.merchant['id'],
                                           customer_id=customer['id'])
        self.assertLen(1, rows)
        self.assertData(customer_user, rows[0])

    def test_user_get(self):
        _, expected = self.user_add(self.merchant['id'])
        actual = self.storage_conn.user_get(expected['id'])
        self.assertData(expected, actual)

    def test_user_get_missing(self):
        self.assertMissing(self.storage_conn.user_get, UUID)

    def test_user_update(self):
        fixture, data = self.user_add(self.merchant['id'])

        fixture['username'] = 'test'
        updated = self.storage_conn.user_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_user_update_missing(self):
        self.assertMissing(self.storage_conn.user_update, UUID, {})

    def test_user_delete(self):
        _, data = self.user_add(self.merchant['id'])
        self.storage_conn.user_delete(data['id'])
        self.assertMissing(self.storage_conn.user_get, data['id'])

    def test_user_delete_missing(self):
        self.assertMissing(self.storage_conn.user_delete, UUID)

    # Products
    def test_product_add(self):
        f, data = self.product_add(self.merchant['id'])
        self.assertData(f, data)

    def test_product_get(self):
        f, expected = self.product_add(self.merchant['id'])
        actual = self.storage_conn.product_get(expected['id'])
        self.assertData(expected, actual)

    def test_product_get_missing(self):
        self.assertMissing(self.storage_conn.product_get, UUID)

    def test_product_update(self):
        fixture, data = self.product_add(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.product_update(data['id'], fixture)

        self.assertData(fixture, updated)

    def test_product_update_missing(self):
        self.assertMissing(self.storage_conn.product_update, UUID, {})

    def test_product_delete(self):
        f, data = self.product_add(self.merchant['id'])
        self.storage_conn.product_delete(data['id'])
        self.assertMissing(self.storage_conn.product_get, data['id'])

    def test_product_delete_missing(self):
        self.assertMissing(self.storage_conn.product_delete, UUID)
