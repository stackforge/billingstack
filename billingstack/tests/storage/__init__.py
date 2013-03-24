# -*- encoding: utf-8 -*-
#
# Author: Endre Karlson <endre.karlson@gmail.com>
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

    def create_language(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_language(ctxt, fixture, **kw)

    def create_currency(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_currency(ctxt, fixture, **kw)

    def pg_provider_register(self, fixture=0, values={}, methods=[], **kw):
        methods = [self.get_fixture('pg_method')] or methods
        fixture = self.get_fixture('pg_provider', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.storage_conn.pg_provider_register(
            ctxt, fixture, methods=methods, **kw)

        fixture['methods'] = methods
        return fixture, data

    def create_pg_method(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_method')
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_pg_method(ctxt, fixture)

    def create_merchant(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.storage_conn.create_merchant(ctxt, fixture, **kw)

    def create_pg_config(self, merchant_id, fixture=0, values={},
                         **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_pg_config(
            ctxt, merchant_id, fixture, **kw)

    def create_customer(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.storage_conn.create_customer(
            ctxt, merchant_id, fixture, **kw)

    def create_payment_method(self, customer_id, fixture=0,
                              values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_payment_method(
            ctxt, customer_id, fixture, **kw)

    def create_product(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('product', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_product(
            ctxt, merchant_id, fixture, **kw)

    def create_plan(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('plan', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_plan(
            ctxt, merchant_id, fixture, **kw)

    # Currencies
    def test_create_currency(self):
        self.assertDuplicate(self.create_currency)

    # Languages
    def test_create_language(self):
        self.assertDuplicate(self.create_language)

    def test_set_properties(self):
        fixture, data = self.create_product(self.merchant['id'])

        metadata = {"random": True}
        self.storage_conn.set_properties(data['id'], metadata,
                                         cls=models.Product)

        metadata.update({'foo': 1, 'bar': 2})
        self.storage_conn.set_properties(data['id'], metadata,
                                         cls=models.Product)

        actual = self.storage_conn.get_product(self.admin_ctxt, data['id'])
        self.assertLen(6, actual['properties'])

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
        self.storage_conn.create_pg_method(self.admin_ctxt, method1)

        method2 = {'type': 'creditcard', 'name': 'amex'}
        self.storage_conn.create_pg_method(self.admin_ctxt, method2)

        method3 = {'type': 'creditcard', 'name': 'visa'}

        methods = [method1, method2, method3]
        provider = {'name': 'noop'}

        provider = self.storage_conn.pg_provider_register(
            self.admin_ctxt, provider, methods)

        # TODO(ekarls): Make this more extensive?
        self.assertLen(3, provider['methods'])

    def test_get_pg_provider(self):
        _, expected = self.pg_provider_register()
        actual = self.storage_conn.get_pg_provider(self.admin_ctxt,
                                                   expected['id'])
        self.assertData(expected, actual)

    def test_get_pg_provider_missing(self):
        self.assertMissing(self.storage_conn.get_pg_provider,
                           self.admin_ctxt, UUID)

    def test_pg_provider_deregister(self):
        _, data = self.pg_provider_register()
        self.storage_conn.pg_provider_deregister(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.pg_provider_deregister,
                           self.admin_ctxt, data['id'])

    def test_pg_provider_deregister_missing(self):
        self.assertMissing(self.storage_conn.pg_provider_deregister,
                           self.admin_ctxt, UUID)

    # Payment Gateway Configuration
    def test_create_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {'provider_id': provider['id']}
        fixture, data = self.create_pg_config(
            self.merchant['id'], values=values)

        self.assertData(fixture, data)

    def test_get_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {'provider_id': provider['id']}

        fixture, data = self.create_pg_config(
            self.merchant['id'], values=values)

    def test_get_pg_config_missing(self):
        self.assertMissing(self.storage_conn.get_pg_config,
                           self.admin_ctxt, UUID)

    def test_update_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {'provider_id': provider['id']}

        fixture, data = self.create_pg_config(
            self.merchant['id'], values=values)

        fixture['properties'] = {"api": 1}
        updated = self.storage_conn.update_pg_config(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_pg_config_missing(self):
        _, provider = self.pg_provider_register()

        values = {'provider_id': provider['id']}

        fixture, data = self.create_pg_config(
            self.merchant['id'], values=values)

        self.assertMissing(self.storage_conn.update_pg_config,
                           self.admin_ctxt, UUID, {})

    def test_delete_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {'provider_id': provider['id']}

        fixture, data = self.create_pg_config(
            self.merchant['id'], values=values)

        self.storage_conn.delete_pg_config(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_pg_config,
                           self.admin_ctxt, data['id'])

    def test_delete_pg_config_missing(self):
        self.assertMissing(self.storage_conn.delete_pg_config,
                           self.admin_ctxt, UUID)

    # PaymentMethod
    def test_create_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()
        _, config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': provider['id']})
        _, customer = self.create_customer(self.merchant['id'])

        # Setup PaymentMethod
        values = {
            'provider_method_id': provider['methods'][0]['id'],
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(
            customer['id'], values=values)
        self.assertData(fixture, data)

    def test_get_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()
        _, config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': provider['id']})
        _, customer = self.create_customer(self.merchant['id'])

        # Setup PaymentMethod
        values = {
            'provider_method_id': provider['methods'][0]['id'],
            'provider_config_id': config['id']}

        _, expected = self.create_payment_method(
            customer['id'], values=values)
        actual = self.storage_conn.get_payment_method(self.admin_ctxt,
                                                      expected['id'])
        self.assertData(expected, actual)

    # TODO(ekarlso): Make this test more extensive?
    def test_list_payment_methods(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()
        _, config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': provider['id']})

        values = {
            'provider_method_id': provider['methods'][0]['id'],
            'provider_config_id': config['id']}

        # Add two Customers with some methods
        _, customer1 = self.create_customer(self.merchant['id'])
        self.create_payment_method(
            customer1['id'], values=values)
        rows = self.storage_conn.list_payment_methods(
            self.admin_ctxt,
            criterion={'customer_id': customer1['id']})
        self.assertLen(1, rows)

        _, customer2 = self.create_customer(self.merchant['id'])
        self.create_payment_method(
            customer2['id'], values=values)
        self.create_payment_method(
            customer2['id'], values=values)
        rows = self.storage_conn.list_payment_methods(
            self.admin_ctxt,
            criterion={'customer_id': customer2['id']})
        self.assertLen(2, rows)

    def test_get_payment_method_missing(self):
        self.assertMissing(self.storage_conn.get_payment_method,
                           self.admin_ctxt, UUID)

    def test_update_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()
        _, config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': provider['id']})
        _, customer = self.create_customer(self.merchant['id'])

        # Setup PaymentMethod
        values = {
            'provider_method_id': provider['methods'][0]['id'],
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(
            customer['id'], values=values)

        fixture['identifier'] = 1
        updated = self.storage_conn.update_payment_method(self.admin_ctxt,
                                                          data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_payment_method_missing(self):
        self.assertMissing(self.storage_conn.update_payment_method,
                           self.admin_ctxt, UUID, {})

    def test_delete_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()
        _, config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': provider['id']})
        _, customer = self.create_customer(self.merchant['id'])

        # Setup PaymentMethod
        values = {
            'provider_method_id': provider['methods'][0]['id'],
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(
            customer['id'], values=values)

        self.storage_conn.delete_payment_method(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_payment_method,
                           self.admin_ctxt, data['id'])

    def test_delete_payment_method_missing(self):
        self.assertMissing(self.storage_conn.delete_payment_method,
                           self.admin_ctxt, UUID)

    # Merchant
    def test_create_merchant(self):
        fixture, data = self.create_merchant()
        self.assertData(fixture, data)

    def test_get_merchant(self):
        _, expected = self.create_merchant()
        actual = self.storage_conn.get_merchant(
            self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_get_merchant_missing(self):
        self.assertMissing(self.storage_conn.get_merchant,
                           self.admin_ctxt, UUID)

    def test_update_merchant(self):
        fixture, data = self.create_merchant()

        fixture['name'] = 'test'
        updated = self.storage_conn.update_merchant(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_merchant_missing(self):
        self.assertMissing(self.storage_conn.update_merchant,
                           self.admin_ctxt, UUID, {})

    def test_delete_merchant(self):
        self.storage_conn.delete_merchant(self.admin_ctxt, self.merchant['id'])
        self.assertMissing(self.storage_conn.get_merchant,
                           self.admin_ctxt, self.merchant['id'])

    def test_delete_merchant_missing(self):
        self.assertMissing(self.storage_conn.delete_merchant,
                           self.admin_ctxt, UUID)

    # Customer
    def test_create_customer(self):
        fixture, data = self.create_customer(self.merchant['id'])
        assert data['default_info'] == {}
        assert data['contact_info'] == []
        self.assertData(fixture, data)

    def test_create_customer_with_contact_info(self):
        contact_fixture = self.get_fixture('contact_info')
        customer_fixture, data = self.create_customer(
            self.merchant['id'],
            values={'contact_info': contact_fixture})
        self.assertData(customer_fixture, data)
        self.assertData(contact_fixture, data['default_info'])
        self.assertData(contact_fixture, data['contact_info'][0])

    def test_get_customer(self):
        _, expected = self.create_customer(self.merchant['id'])
        actual = self.storage_conn.get_customer(
            self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_get_customer_missing(self):
        self.assertMissing(self.storage_conn.get_customer,
                           self.admin_ctxt, UUID)

    def test_update_customer(self):
        fixture, data = self.create_customer(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.update_customer(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_customer_missing(self):
        self.assertMissing(self.storage_conn.update_customer,
                           self.admin_ctxt, UUID, {})

    def test_delete_customer(self):
        _, data = self.create_customer(self.merchant['id'])
        self.storage_conn.delete_customer(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_customer,
                           self.admin_ctxt, data['id'])

    def test_delete_customer_missing(self):
        self.assertMissing(self.storage_conn.delete_customer,
                           self.admin_ctxt, UUID)

    # Products
    def test_create_product(self):
        f, data = self.create_product(self.merchant['id'])
        self.assertData(f, data)

    def test_get_product(self):
        f, expected = self.create_product(self.merchant['id'])
        actual = self.storage_conn.get_product(self.admin_ctxt, expected['id'])
        self.assertData(expected, actual)

    def test_get_product_missing(self):
        self.assertMissing(self.storage_conn.get_product,
                           self.admin_ctxt, UUID)

    def test_update_product(self):
        fixture, data = self.create_product(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.update_product(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_product_missing(self):
        self.assertMissing(self.storage_conn.update_product,
                           self.admin_ctxt, UUID, {})

    def test_delete_product(self):
        fixture, data = self.create_product(self.merchant['id'])
        self.storage_conn.delete_product(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_product,
                           self.admin_ctxt, data['id'])

    def test_delete_product_missing(self):
        self.assertMissing(self.storage_conn.delete_product,
                           self.admin_ctxt, UUID)

    # Plan
    def test_create_plan_with_items(self):
        _, p1 = self.create_product(self.merchant['id'])
        _, p2 = self.create_product(self.merchant['id'])

        values = {
            'plan_items': [{'product_id': p1['id']}, {'product_id': p2['id']}]
        }

        fixture, data = self.create_plan(self.merchant['id'], values=values)
        self.assertData(fixture, data)

    def test_create_plan_without_items(self):
        fixture, data = self.create_plan(self.merchant['id'])
        self.assertData(fixture, data)

    def test_get_plan(self):
        fixture, data = self.create_plan(self.merchant['id'])
        actual = self.storage_conn.get_plan(self.admin_ctxt, data['id'])

        # FIXME(ekarlso): This should test the actual items also? But atm
        # there's am error that if the value is int when getting added it's
        # string when returned...
        self.assertEqual(data['name'], actual['name'])
        self.assertEqual(data['title'], actual['title'])
        self.assertEqual(data['description'], actual['description'])

    def test_get_plan_missing(self):
        self.assertMissing(self.storage_conn.get_plan, self.admin_ctxt, UUID)

    def test_update_plan(self):
        fixture, data = self.create_plan(self.merchant['id'])

        fixture['name'] = 'test'
        updated = self.storage_conn.update_plan(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_plan_missing(self):
        self.assertMissing(self.storage_conn.update_plan,
                           self.admin_ctxt, UUID, {})

    def test_delete_plan(self):
        fixture, data = self.create_plan(self.merchant['id'])
        self.storage_conn.delete_plan(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_plan,
                           self.admin_ctxt, data['id'])

    def test_delete_plan_missing(self):
        self.assertMissing(self.storage_conn.delete_plan,
                           self.admin_ctxt, UUID)
