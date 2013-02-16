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
from billingstack.tests.base import TestCase
from billingstack import exceptions
from billingstack import storage

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

    # Merchant
    def test_merchant_add(self):
        f, data = self.merchant_add()
        self.assertData(f, data)

    def test_merchant_get(self):
        _, expected = self.merchant_add()
        actual = self.storage_conn.merchant_get(expected['id'])
        self.assertData(expected, actual)

    def test_merchant_get_missing(self):
        self.assertMissing(self.storage_conn.merchant_get, UUID)

    def test_merchant_update(self):
        fixture, data = self.merchant_add()
        updated = self.storage_conn.merchant_update(data['id'], fixture)
        self.assertData(data, updated)

    def test_merchant_update_missing(self):
        self.assertMissing(self.storage_conn.merchant_update, UUID, {})

    def test_merchant_delete(self):
        self.storage_conn.merchant_delete(self.merchant['id'])
        self.assertMissing(self.storage_conn.merchant_get, self.merchant['id'])

    def test_merchant_delete_missing(self):
        self.assertMissing(self.storage_conn.merchant_delete, UUID)

    # Payment Gateways
    def test_payment_gw_add(self):
        fixture, actual = self.payment_gw_add(self.merchant['id'])
        self.assertData(fixture, actual)

    def test_payment_gw_get(self):
        _, expected = self.payment_gw_add(self.merchant['id'])
        actual = self.storage_conn.payment_gw_get(expected['id'])
        self.assertData(expected, actual)

    def test_payment_gw_get_missing(self):
        self.assertMissing(self.storage_conn.payment_gw_get, UUID)

    def test_payment_gw_update(self):
        fixture, data = self.payment_gw_add(self.merchant['id'])
        fixture['configuration'] = {}
        updated = self.storage_conn.payment_gw_update(data['id'], fixture)
        self.assertData(fixture, updated)

    def test_payment_gw_update_missing(self):
        self.assertMissing(self.storage_conn.payment_gw_update, UUID, {})

    def test_payment_gw_delete(self):
        _, data = self.payment_gw_add(self.merchant['id'])
        self.storage_conn.payment_gw_delete(data['id'])
        self.assertMissing(self.storage_conn.payment_gw_get, data['id'])

    def test_payment_gw_delete_missing(self):
        self.assertMissing(self.storage_conn.payment_gw_delete, UUID)

    # Customer
    def test_customer_add(self):
        fixture, data = self.customer_add(self.merchant['id'])
        self.assertData(fixture, data)

    def test_customer_get(self):
        _, expected = self.customer_add(self.merchant['id'])
        actual = self.storage_conn.customer_get(expected['id'])
        self.assertData(expected, actual)

    def test_customer_get_missing(self):
        self.assertMissing(self.storage_conn.customer_get, UUID)

    def test_customer_update(self):
        fixture, data = self.customer_add(self.merchant['id'])
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
        self.assertData(fixture, data)

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
