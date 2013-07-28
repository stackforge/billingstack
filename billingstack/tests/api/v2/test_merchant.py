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
"""
Test Merchants
"""

from billingstack.tests.api.v2 import V2Test
from billingstack.api.v2.models import Merchant


class TestMerchant(V2Test):
    __test__ = True

    def fixture(self):
        fixture = self.get_fixture('merchant')
        self._account_defaults(fixture)
        expected = Merchant.from_db(fixture).as_dict()
        return expected

    def test_create_merchant(self):
        expected = self.fixture()

        resp = self.post('merchants', expected)

        self.assertData(expected, resp.json)

    def test_list_merchants(self):
        resp = self.get('merchants')
        self.assertLen(1, resp.json)

    def test_get_merchant(self):
        expected = Merchant.from_db(self.merchant).as_dict()

        resp = self.get('merchants/' + self.merchant['id'])

        self.assertData(expected, resp.json)

    def test_update_merchant(self):
        expected = Merchant.from_db(self.merchant).as_dict()

        resp = self.patch_('merchants/' + self.merchant['id'], expected)

        self.assertData(expected, resp.json)

    def test_delete_merchant(self):
        self.delete('merchants/' + self.merchant['id'])
        self.assertLen(0, self.services.central.list_merchants(
                       self.admin_ctxt))
