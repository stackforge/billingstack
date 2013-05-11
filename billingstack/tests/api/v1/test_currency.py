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
# License for the specific currency governing permissions and limitations
# under the License.
"""
Test Currency
"""

import logging

from billingstack.tests.api.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestCurrency(FunctionalTest):
    __test__ = True
    path = "currencies"

    def test_create_currency(self):
        fixture = self.get_fixture('currency', fixture=1)

        resp = self.post(self.path, fixture)

        self.assertData(fixture, resp.json)

    def test_list_currencies(self):

        resp = self.get(self.path)

        self.assertLen(1, resp.json)

    def test_get_currency(self):
        _, currency = self.create_currency(fixture=1)

        url = self.item_path(currency['name'])
        resp = self.get(url)

        self.assertData(resp.json, currency)

    def test_update_currency(self):
        _, currency = self.create_currency(fixture=1)

        url = self.item_path(currency['name'])
        resp = self.put(url, currency)

        self.assertData(resp.json, currency)

    def test_delete_currency(self):
        _, currency = self.create_currency(fixture=1)

        url = self.item_path(currency['name'])
        self.delete(url)

        data = self.services.central.list_currencies(self.admin_ctxt)
        self.assertLen(1, data)
