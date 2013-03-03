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

    def setUp(self):
        super(StorageDriverTestCase, self).setUp()
        self.storage_conn = self.get_storage_driver()
        self.setSamples()

    def language_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.language_add(ctxt, fixture, **kw)

    def currency_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.currency_add(ctxt, fixture, **kw)

    def pg_provider_register(self, fixture=0, values={}, methods=[], **kw):
        methods = [self.get_fixture('pg_method')] or methods
        fixture = self.get_fixture('pg_provider', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.storage_conn.pg_provider_register(ctxt, fixture, methods=methods, **kw)

        fixture['methods'] = methods
        return fixture, data

    def pg_method_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_method')
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.pg_method_add(ctxt, fixture)

    def _account_defaults(self, values):
        # NOTE: Do defaults
        if not 'currency_id' in values:
            values['currency_id'] = self.currency['id']

        if not 'language_id' in values:
            values['language_id'] = self.language['id']

    def merchant_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.storage_conn.merchant_add(ctxt, fixture, **kw)

    def pg_config_add(self, provider_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.pg_config_add(ctxt, self.merchant['id'], provider_id, fixture, **kw)

    def customer_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.storage_conn.customer_add(ctxt, merchant_id, fixture, **kw)

    def payment_method_add(self, customer_id, provider_method_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.payment_method_add(
            ctxt, customer_id, provider_method_id, fixture, **kw)

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('user', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.user_add(ctxt, merchant_id, fixture, **kw)

    def product_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('product', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.product_add(ctxt, merchant_id, fixture, **kw)

    def plan_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('plan', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.plan_add(ctxt, merchant_id, fixture, **kw)

    # Currencies
    def test_currency_add(self):
        self.assertDuplicate(self.currency_add)

    # Languages
    def test_language_add(self):
        self.assertDuplicate(self.language_add)

    def test_set_properties(self):
        fixture, data = self.product_add(self.merchant['id'])

        metadata = {"random": True}
        self.storage_conn.set_properties(data['id'], metadata, cls=models.Product)

        metadata.update({'foo': 1, 'bar': 2})
        self.storage_conn.set_properties(data['id'], metadata, cls=models.Product)

        actual = self.storage_conn.product_get(self.admin_ctxt, data['id'])
        self.assertLen(4, actual['properties'])

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
        self.storage_conn.pg_method_add(self.admin_ctxt, method1)

        method2 = {'type': 'creditcard', 'name': 'amex'}
        self.storage_conn.pg_method_add(self.admin_ctxt, method2)

        method3 = {'type': 'creditcard', 'name': 'visa', 'owned': 1}

        methods = [method1, method2, method3]
        provider = {'name': 'noop'}

        provider = self.storage_conn.pg_provider_register(self.admin_ctxt, provider, methods)

        # TODO(ekarls): Make this more extensive?
        self.assertLen(3, provider['methods'])

    def test_pg_provider_register_method_switch_methods(self):
        provider_data = {'name': 'noop'}

        system_method = {
            'type': 'creditcard',
            'name': 'mastercard',
            'title': "random"}
        self.storage_conn.pg_method_add(self.admin_ctxt, system_method)

        provider = self.storage_conn.pg_provider_register(
            self.admin_ctxt,
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
            self.admin_ctxt,
            provider_data,
            [provider_method])
        self.assertLen(1, provider['methods'])
        self.assertData(provider_method, provider['methods'][0])

        provider = self.storage_conn.pg_provider_register(
            self.admin_ctxt,
            provider_data,
            [system_method])
        self.assertLen(1, provider['methods'])
        self.assertData(system_method, provider['methods'][0])

    def test_pg_provider_get(self):
        _, expected = self.pg_provider_register()
        actual = self.storage_conn.pg_provider_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_pg_provider_get_missing(self):
        self.assertMissing(self.storage_conn.pg_provider_get, self.admin_ctxt, UUID)

    def test_pg_provider_deregister(self):
        _, data = self.pg_provider_register()
        self.storage_conn.pg_provider_deregister(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.pg_provider_deregister, self.admin_ctxt, data['id'])

    def test_pg_provider_deregister_missing(self):
        self.assertMissing(self.storage_conn.pg_provider_deregister, self.admin_ctxt, UUID)

    # Payment Gateway Configuration
    def test_pg_config_add(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])
        self.assertData(fixture, data)

    def test_pg_config_get(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

    def test_pg_config_get_missing(self):
        self.assertMissing(self.storage_conn.pg_config_get, self.admin_ctxt, UUID)

    def test_pg_config_update(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        fixture['configuration'] = {"api": 1}
        updated = self.storage_conn.pg_config_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_pg_config_update_missing(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.assertMissing(self.storage_conn.pg_config_update, self.admin_ctxt, UUID, {})

    def test_pg_config_delete(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.storage_conn.pg_config_delete(self.admin_ctxt,data['id'])
        self.assertMissing(self.storage_conn.pg_config_get, self.admin_ctxt, data['id'])

    def test_pg_config_delete_missing(self):
        self.assertMissing(self.storage_conn.pg_config_delete, self.admin_ctxt, UUID)

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
        actual = self.storage_conn.payment_method_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    # TODO(ekarlso): Make this test more extensive?
    def test_payment_method_list(self):
        # Setup a PGP with it's sample methods
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']

        # Add two Customers with some methods
        _, customer1 = self.customer_add(self.merchant['id'])
        self.payment_method_add(customer1['id'], m_id)
        rows = self.storage_conn.payment_method_list(
            self.admin_ctxt,
            criterion={'customer_id': customer1['id']})
        self.assertLen(1, rows)

        _, customer2 = self.customer_add(self.merchant['id'])
        self.payment_method_add(customer2['id'], m_id)
        self.payment_method_add(customer2['id'], m_id)

        rows = self.storage_conn.payment_method_list(
            self.admin_ctxt,
            criterion={'customer_id': customer2['id']})
        self.assertLen(2, rows)

    def test_payment_method_get_missing(self):
        self.assertMissing(self.storage_conn.payment_method_get, self.admin_ctxt, UUID)

    def test_payment_method_update(self):
        _, provider = self.pg_provider_register()
        m_id = provider['methods'][0]['id']
        _, customer = self.customer_add(self.merchant['id'])

        fixture, data = self.payment_method_add(customer['id'], m_id)

        fixture['identifier'] = 1
        updated = self.storage_conn.payment_method_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_payment_method_update_missing(self):
        self.assertMissing(self.storage_conn.payment_method_update, self.admin_ctxt, UUID, {})

    def test_payment_method_delete(self):
        _, provider = self.pg_provider_register()
        fixture, data = self.pg_config_add(provider['id'])

        self.storage_conn.pg_config_delete(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.payment_method_delete, self.admin_ctxt, data['id'])

    def test_payment_method_delete_missing(self):
        self.assertMissing(self.storage_conn.payment_method_delete, self.admin_ctxt, UUID)

    # Merchant
    def test_merchant_add(self):
        fixture, data = self.merchant_add()
        self.assertData(fixture, data)

    def test_merchant_get(self):
        _, expected = self.merchant_add()
        actual = self.storage_conn.merchant_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_merchant_get_missing(self):
        self.assertMissing(self.storage_conn.merchant_get, self.admin_ctxt, UUID)

    def test_merchant_update(self):
        fixture, data = self.merchant_add()

        fixture['name'] = 'test'
        updated = self.storage_conn.merchant_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_merchant_update_missing(self):
        self.assertMissing(self.storage_conn.merchant_update, self.admin_ctxt, UUID, {})

    def test_merchant_delete(self):
        self.storage_conn.merchant_delete(self.admin_ctxt, self.merchant['id'])
        self.assertMissing(self.storage_conn.merchant_get, self.admin_ctxt, self.merchant['id'])

    def test_merchant_delete_missing(self):
        self.assertMissing(self.storage_conn.merchant_delete, self.admin_ctxt, UUID)

    # Customer
    def test_customer_add(self):
        fixture, data = self.customer_add(self.merchant['id'])
        assert data['default_info'] == None
        self.assertData(fixture, data)

    def test_customer_add_with_contact_info(self):
        contact_fixture = self.get_fixture('contact_info')
        customer_fixture, data = self.customer_add(
            self.merchant['id'],
            values={'contact_info': contact_fixture})
        self.assertData(customer_fixture, data)
        self.assertData(contact_fixture, data['default_info'])

    def test_customer_get(self):
        _, expected = self.customer_add(self.merchant['id'])
        actual = self.storage_conn.customer_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_customer_get_missing(self):
        self.assertMissing(self.storage_conn.customer_get, self.admin_ctxt, UUID)

    def test_customer_update(self):
        fixture, data = self.customer_add(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.customer_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_customer_update_missing(self):
        self.assertMissing(self.storage_conn.customer_update, self.admin_ctxt, UUID, {})

    def test_customer_delete(self):
        _, data = self.customer_add(self.merchant['id'])
        self.storage_conn.customer_delete(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.customer_get, self.admin_ctxt, data['id'])

    def test_customer_delete_missing(self):
        self.assertMissing(self.storage_conn.customer_delete, self.admin_ctxt, UUID)

    # User
    def test_user_add(self):
        fixture, data = self.user_add(self.merchant['id'])
        assert data['contact_info'] == None
        self.assertData(fixture, data)

    def test_user_add_with_contact_info(self):
        contact_fixture = self.get_fixture('contact_info')
        user_fixture, data = self.user_add(
            self.merchant['id'],
            values={
                'contact_info': contact_fixture})
        self.assertData(user_fixture, data)
        self.assertData(contact_fixture, data['contact_info'])


    def test_user_add_with_customer(self):
        _, customer = self.customer_add(self.merchant['id'])
        fixture, data = self.user_add(
            self.merchant['id'],
            values={
                'customer_id': customer['id']})
        self.assertData(fixture, data)

    def test_user_list(self):
        criterion = {
            "merchant_id": self.merchant['id']
        }

        self.assertLen(0, self.storage_conn.user_list(
            self.admin_ctxt, criterion=criterion))

        self.user_add(self.merchant['id'])

        rows = self.storage_conn.user_list(self.admin_ctxt, criterion=criterion)
        self.assertLen(1, rows)

    def test_user_list_customer(self):
        self.assertLen(0, self.storage_conn.user_list(self.admin_ctxt))

        # NOTE: Add 1 user for the Merchant and 1 with a Customer
        _, merchant_user = self.user_add(self.merchant['id'])

        _, customer = self.customer_add(self.merchant['id'])
        _, customer_user = self.user_add(
            self.merchant['id'],
            values=dict(customer_id=customer['id']))

        criterion = {
            'merchant_id': self.merchant['id'],
            'customer_id': customer['id']}

        rows = self.storage_conn.user_list(self.admin_ctxt, criterion=criterion)
        self.assertLen(1, rows)
        self.assertData(customer_user, rows[0])

    def test_user_get(self):
        _, expected = self.user_add(self.merchant['id'])
        actual = self.storage_conn.user_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_user_get_missing(self):
        self.assertMissing(self.storage_conn.user_get, self.admin_ctxt, UUID)

    def test_user_update(self):
        fixture, data = self.user_add(self.merchant['id'])

        fixture['username'] = 'test'
        updated = self.storage_conn.user_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_user_update_missing(self):
        self.assertMissing(self.storage_conn.user_update, self.admin_ctxt, UUID, {})

    def test_user_delete(self):
        _, data = self.user_add(self.merchant['id'])
        self.storage_conn.user_delete(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.user_get, self.admin_ctxt, data['id'])

    def test_user_delete_missing(self):
        self.assertMissing(self.storage_conn.user_delete, self.admin_ctxt, UUID)

    # Products
    def test_product_add(self):
        f, data = self.product_add(self.merchant['id'])
        self.assertData(f, data)

    def test_product_get(self):
        f, expected = self.product_add(self.merchant['id'])
        actual = self.storage_conn.product_get(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_product_get_missing(self):
        self.assertMissing(self.storage_conn.product_get, self.admin_ctxt, UUID)

    def test_product_update(self):
        fixture, data = self.product_add(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.product_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_product_update_missing(self):
        self.assertMissing(self.storage_conn.product_update, self.admin_ctxt, UUID, {})

    def test_product_delete(self):
        fixture, data = self.product_add(self.merchant['id'])
        self.storage_conn.product_delete(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.product_get, self.admin_ctxt, data['id'])

    def test_product_delete_missing(self):
        self.assertMissing(self.storage_conn.product_delete, self.admin_ctxt, UUID)

    # Plan
    def test_plan_add_with_items(self):
        _, p1 = self.product_add(self.merchant['id'])
        _, p2 = self.product_add(self.merchant['id'])

        values = {
            'plan_items': [{'product_id': p1['id']}, {'product_id': p2['id']}]
        }

        fixture, data = self.plan_add(self.merchant['id'], values=values)
        self.assertData(fixture, data)

    def test_plan_add_without_items(self):
        fixture, data = self.plan_add(self.merchant['id'])
        self.assertData(fixture, data)

    def test_plan_get(self):
        fixture, data = self.plan_add(self.merchant['id'])
        actual = self.storage_conn.plan_get(self.admin_ctxt, data['id'])

        # FIXME(ekarlso): This should test the actual items also? But atm there's an
        # error that if the value is int when getting added it's string when returned...
        self.assertEqual(data['name'], actual['name'])
        self.assertEqual(data['title'], actual['title'])
        self.assertEqual(data['description'], actual['description'])

    def test_plan_get_missing(self):
        self.assertMissing(self.storage_conn.plan_get, self.admin_ctxt, UUID)

    def test_plan_update(self):
        fixture, data = self.plan_add(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.plan_update(self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_plan_update_missing(self):
        self.assertMissing(self.storage_conn.plan_update, self.admin_ctxt, UUID, {})

    def test_plan_delete(self):
        fixture, data = self.plan_add(self.merchant['id'])
        self.storage_conn.plan_delete(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.plan_get, self.admin_ctxt, data['id'])

    def test_plan_delete_missing(self):
        self.assertMissing(self.storage_conn.plan_delete, self.admin_ctxt, UUID)