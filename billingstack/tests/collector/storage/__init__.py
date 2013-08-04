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
from billingstack.openstack.common.uuidutils import generate_uuid


LOG = logging.getLogger(__name__)


UUID = generate_uuid()
MERCHANT_UUID = generate_uuid()
CUSTOMER_UUID = generate_uuid()


class DriverMixin(object):
    def pg_provider_register(self, fixture=0, values={}, methods=[], **kw):
        methods = [self.get_fixture('pg_method')] or methods
        if not 'methods' in values:
            values['methods'] = methods

        fixture = self.get_fixture('pg_provider', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.storage_conn.pg_provider_register(
            ctxt, fixture.copy(), **kw)

        return fixture, data

    def create_pg_config(self, fixture=0, values={},
                         **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_pg_config(
            ctxt, fixture, **kw)

    def create_payment_method(self, fixture=0,
                              values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_payment_method(
            ctxt, fixture, **kw)

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
        method2 = {'type': 'creditcard', 'name': 'amex'}
        method3 = {'type': 'creditcard', 'name': 'visa'}

        provider = {'name': 'noop', 'methods': [method1, method2, method3]}

        provider = self.storage_conn.pg_provider_register(
            self.admin_ctxt, provider)

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

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']}
        fixture, data = self.create_pg_config(values=values)

        self.assertData(fixture, data)

    def test_get_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']}

        fixture, data = self.create_pg_config(values=values)

    def test_get_pg_config_missing(self):
        self.assertMissing(self.storage_conn.get_pg_config,
                           self.admin_ctxt, UUID)

    def test_update_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']}
        fixture, data = self.create_pg_config(values=values)

        fixture['properties'] = {"api": 1}
        updated = self.storage_conn.update_pg_config(
            self.admin_ctxt, data['id'], fixture)

        self.assertData(fixture, updated)

    def test_update_pg_config_missing(self):
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']}

        fixture, data = self.create_pg_config(values=values)

        self.assertMissing(self.storage_conn.update_pg_config,
                           self.admin_ctxt, UUID, {})

    def test_delete_pg_config(self):
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']}

        fixture, data = self.create_pg_config(values=values)

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

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']
        }
        _, config = self.create_pg_config(values=values)

        # Setup PaymentMethod
        values = {
            'customer_id': CUSTOMER_UUID,
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(values=values)
        self.assertData(fixture, data)

    def test_get_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']
        }
        _, config = self.create_pg_config(values=values)

        # Setup PaymentMethod
        values = {
            'customer_id': CUSTOMER_UUID,
            'provider_config_id': config['id']}

        _, expected = self.create_payment_method(values=values)
        actual = self.storage_conn.get_payment_method(self.admin_ctxt,
                                                      expected['id'])
        self.assertData(expected, actual)

    # TODO(ekarlso): Make this test more extensive?
    def test_list_payment_methods(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']
        }
        _, config = self.create_pg_config(values=values)

        # Add two Customers with some methods
        customer1_id = generate_uuid()
        values = {
            'customer_id': customer1_id,
            'provider_config_id': config['id']}
        self.create_payment_method(values=values)
        rows = self.storage_conn.list_payment_methods(
            self.admin_ctxt,
            criterion={'customer_id': customer1_id})
        self.assertLen(1, rows)

        customer2_id = generate_uuid()
        values = {
            'customer_id': customer2_id,
            'provider_config_id': config['id']}
        self.create_payment_method(values=values)
        self.create_payment_method(values=values)
        rows = self.storage_conn.list_payment_methods(
            self.admin_ctxt,
            criterion={'customer_id': customer2_id})
        self.assertLen(2, rows)

    def test_get_payment_method_missing(self):
        self.assertMissing(self.storage_conn.get_payment_method,
                           self.admin_ctxt, UUID)

    def test_update_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']
        }
        _, config = self.create_pg_config(values=values)

        # Setup PaymentMethod
        values = {
            'customer_id': CUSTOMER_UUID,
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(values=values)

        fixture['identifier'] = 1
        updated = self.storage_conn.update_payment_method(
            self.admin_ctxt,
            data['id'],
            fixture)

        self.assertData(fixture, updated)

    def test_update_payment_method_missing(self):
        self.assertMissing(self.storage_conn.update_payment_method,
                           self.admin_ctxt, UUID, {})

    def test_delete_payment_method(self):
        # Setup pgp / pgm / pgc
        _, provider = self.pg_provider_register()

        values = {
            'merchant_id': MERCHANT_UUID,
            'provider_id': provider['id']
        }
        _, config = self.create_pg_config(values=values)

        # Setup PaymentMethod
        values = {
            'customer_id': CUSTOMER_UUID,
            'provider_config_id': config['id']}

        fixture, data = self.create_payment_method(values=values)

        self.storage_conn.delete_payment_method(self.admin_ctxt, data['id'])
        self.assertMissing(self.storage_conn.get_payment_method,
                           self.admin_ctxt, data['id'])

    def test_delete_payment_method_missing(self):
        self.assertMissing(self.storage_conn.delete_payment_method,
                           self.admin_ctxt, UUID)
