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
#
"""Test listing raw events.
"""

from billingstack.tests.api.v1.base import FunctionalTest
from billingstack.api.v1.models import Customer


class TestCustomer(FunctionalTest):
    __test__ = True
    path = "merchants/%s/customers"

    def fixture(self):
        fixture = self.get_fixture('customer')
        self._account_defaults(fixture)
        expected = Customer.from_db(fixture).as_dict()
        return expected

    def test_customer_add(self):
        expected = self.fixture()

        url = self.path % self.merchant['id']

        resp = self.post(url, expected)

        self.assertData(expected, resp.json)

    def test_customer_list(self):
        url = self.path % self.merchant['id']

        resp = self.get(url)
        self.assertLen(0, resp.json)

        self.customer_add(self.merchant['id'])

        resp = self.get(url)
        self.assertLen(1, resp.json)

    def test_customer_get(self):
        _, customer = self.customer_add(self.merchant['id'])

        expected = Customer.from_db(customer).as_dict()

        url = self.item_path(self.merchant['id'], customer['id'])
        resp = self.get(url)

        self.assertData(expected, resp.json)

    def test_customer_update(self):
        _, customer = self.customer_add(self.merchant['id'])

        expected = Customer.from_db(customer).as_dict()

        expected['name'] = 'test'

        url = self.item_path(self.merchant['id'], customer['id'])
        resp = self.put(url, customer)

        self.assertData(resp.json, customer)

    def test_customer_delete(self):
        _, customer = self.customer_add(self.merchant['id'])

        url = self.item_path(self.merchant['id'], customer['id'])
        self.delete(url)

        self.assertLen(0, self.central_service.customer_list(self.admin_ctxt))
