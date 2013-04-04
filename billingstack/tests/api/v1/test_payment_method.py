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
Test Products
"""

import logging

from billingstack.tests.api.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestPaymentMethod(FunctionalTest):
    __test__ = True
    path = "merchants/%s/customers/%s/payment-methods"

    def setUp(self):
        super(TestPaymentMethod, self).setUp()
        _, self.provider = self.pg_provider_register()

        _, self.customer = self.create_customer(self.merchant['id'])
        _, self.pg_config = self.create_pg_config(
            self.merchant['id'], values={'provider_id': self.provider['id']})

    def test_create_payment_method(self):
        fixture = self.get_fixture('payment_method')
        fixture['provider_config_id'] = self.pg_config['id']

        url = self.path % (self.merchant['id'], self.customer['id'])

        resp = self.post(url, fixture)

        self.assertData(fixture, resp.json)

    def test_list_payment_methods(self):
        values = {
            'provider_config_id': self.pg_config['id']
        }
        self.create_payment_method(self.customer['id'], values=values)

        url = self.path % (self.merchant['id'], self.customer['id'])
        resp = self.get(url)

        self.assertLen(1, resp.json)

    def test_get_payment_method(self):
        values = {
            'provider_config_id': self.pg_config['id']
        }
        _, method = self.create_payment_method(
            self.customer['id'], values=values)

        url = self.item_path(self.merchant['id'],
                             self.customer['id'], method['id'])

        resp = self.get(url)

        self.assertData(resp.json, method)

    def test_update_payment_method(self):
        values = {
            'provider_config_id': self.pg_config['id']
        }
        fixture, method = self.create_payment_method(
            self.customer['id'], values=values)

        url = self.item_path(self.merchant['id'],
                             self.customer['id'], method['id'])

        expected = dict(fixture, name='test2')
        resp = self.put(url, expected)
        self.assertData(expected, resp.json)

    def test_delete_payment_method(self):
        values = {
            'provider_config_id': self.pg_config['id']
        }
        _, method = self.create_payment_method(
            self.customer['id'], values=values)

        url = self.item_path(self.merchant['id'],
                             self.customer['id'], method['id'])
        self.delete(url)

        self.assertLen(0, self.central_service.list_products(self.admin_ctxt))
