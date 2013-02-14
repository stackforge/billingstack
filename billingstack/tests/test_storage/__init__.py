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
# Copied: billingstack
from billingstack.openstack.common import log as logging
from billingstack.tests import TestCase
from billingstack import exceptions
from billingstack import storage

LOG = logging.getLogger(__name__)


UUID = 'caf771fc-6b05-4891-bee1-c2a48621f57b'


class StorageTestCase(TestCase):
    __test__ = False

    def get_storage_driver(self):
        connection = storage.get_connection()
        return connection


class StorageDriverTestCase(StorageTestCase):
    def setUp(self):
        super(StorageDriverTestCase, self).setUp()
        self.storage_conn = self.get_storage_driver()

        _, self.currency = self.currency_add()
        _, self.language = self.language_add()
        _, self.merchant = self.merchant_add()

    def language_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        return fixture, self.storage_conn.language_add(fixture, **kw)

    def currency_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        return fixture, self.storage_conn.currency_add(fixture, **kw)

    def _account_defaults(self, values):
        # NOTE: Do defaults
        if not 'currency_id' in values:
            values['currency_id'] = self.currency['id']

        if not 'language_id' in values:
            values['language_id'] = self.language['id']

    def merchant_add(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        self._account_defaults(fixture)
        return fixture, self.storage_conn.merchant_add(fixture, **kw)

    def customer_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        self._account_defaults(fixture)
        return fixture, self.storage_conn.customer_add(merchant_id, fixture, **kw)

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('user', fixture, values)
        return fixture, self.storage_conn.user_add(merchant_id, fixture, **kw)

    def _raises(self, func, exception, *args, **kw):
        """
        Exec function with assertRaises

        :param func: Function to run
        :para
        """
        with self.assertRaises(exception):
            func(*args, **kw)

    def _duplicate(self, func, exception=None, *args, **kw):
        """
        Asserts that func will raise a Duplicate
        """
        exception = kw.pop('exception', exceptions.Duplicate)
        self._raises(func, exception, *args, **kw)

    def _missing(self, func, *args, **kw):
        """
        Asserts that func will raise a NotFound
        """
        exception = kw.pop('exception', exceptions.NotFound)
        self._raises(func, exception, *args, **kw)

    # Currencies
    def test_currency_add_duplicate(self):
        self._duplicate(self.currency_add)

    # Languages
    def test_language_add_duplicate(self):
        self._duplicate(self.language_add)

    # Merchant
    def test_merchant_add(self):
        f, data = self.merchant_add()
        self.assertData(f, data)

    def test_merchant_get(self):
        f, expected = self.merchant_add()
        actual = self.storage_conn.merchant_get(expected['id'])
        self.assertData(expected, actual)

    def test_merchant_get_missing(self):
        self._missing(self.storage_conn.merchant_get, UUID)

    def test_merchant_update(self):
        f, obj = self.merchant_add()
        updated = self.storage_conn.merchant_update(obj['id'], f)
        self.assertData(obj, updated)

    def test_merchant_update_missing(self):
        self._missing(self.storage_conn.merchant_update, UUID, {})

    def test_merchant_delete(self):
        self.storage_conn.merchant_delete(self.merchant['id'])
        self._missing(self.storage_conn.merchant_get, self.merchant['id'])

    def test_merchant_delete_missing(self):
        self._missing(self.storage_conn.merchant_delete, UUID)

    # Customer
    def test_customer_add(self):
        f, data = self.customer_add(self.merchant['id'])
        self.assertData(f, data)

    def test_customer_get(self):
        f, expected = self.customer_add(self.merchant['id'])
        actual = self.storage_conn.customer_get(expected['id'])
        self.assertData(expected, actual)

    def test_customer_get_missing(self):
        self._missing(self.storage_conn.customer_get, UUID)

    def test_customer_update(self):
        f, obj = self.customer_add(self.merchant['id'])
        updated = self.storage_conn.customer_update(obj['id'], f)
        self.assertData(obj, updated)

    def test_customer_update_missing(self):
        self._missing(self.storage_conn.customer_update, UUID, {})

    def test_customer_delete(self):
        f, obj = self.customer_add(self.merchant['id'])
        self.storage_conn.customer_delete(obj['id'])
        self._missing(self.storage_conn.customer_get, obj['id'])

    def test_customer_delete_missing(self):
        self._missing(self.storage_conn.customer_delete, UUID)

    # User
    def test_user_add(self):
        f, data = self.user_add(self.merchant['id'])
        self.assertData(f, data)

    def test_user_add_with_customer(self):
        _, customer = self.customer_add(self.merchant['id'])
        f, data = self.user_add(self.merchant['id'], customer_id=customer['id'])
        self.assertData(f, data)

    def test_user_get(self):
        f, expected = self.user_add(self.merchant['id'])
        actual = self.storage_conn.user_get(expected['id'])
        self.assertData(expected, actual)

    def test_user_get_missing(self):
        self._missing(self.storage_conn.user_get, UUID)

    def test_user_update(self):
        f, user = self.user_add(self.merchant['id'])
        updated = self.storage_conn.user_update(user['id'], f)
        self.assertData(user, updated)

    def test_user_update_missing(self):
        self._missing(self.storage_conn.user_update, UUID, {})

    def test_user_delete(self):
        f, user = self.user_add(self.merchant['id'])
        self.storage_conn.user_delete(user['id'])

        self._missing(self.storage_conn.user_get, user['id'])

    def test_user_delete_missing(self):
        self._missing(self.storage_conn.user_delete, UUID)
