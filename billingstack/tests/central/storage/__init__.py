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
from billingstack.central.storage.impl_sqlalchemy import models


LOG = logging.getLogger(__name__)


UUID = 'caf771fc-6b05-4891-bee1-c2a48621f57b'


class DriverMixin(object):
    def create_language(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_language(ctxt, fixture, **kw)

    def create_currency(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.storage_conn.create_currency(ctxt, fixture, **kw)

    def create_merchant(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.storage_conn.create_merchant(ctxt, fixture, **kw)

    def create_customer(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.storage_conn.create_customer(
            ctxt, merchant_id, fixture, **kw)

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
    def test_create_plan(self):
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
