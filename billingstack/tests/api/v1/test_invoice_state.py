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
Test InvoiceState
"""

import logging

from billingstack.tests.api.v1.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestInvoiceState(FunctionalTest):
    __test__ = True
    path = "invoice-states"

    def test_create_invoice_state(self):
        fixture = self.get_fixture('invoice_state')

        resp = self.post(self.path, fixture)

        self.assertData(fixture, resp.json)

    def test_list_invoice_state(self):
        self.create_invoice_state()

        resp = self.get(self.path)

        self.assertLen(1, resp.json)

    def test_get_invoice_state(self):
        _, state = self.create_invoice_state()

        url = self.item_path(state['name'])
        resp = self.get(url)

        self.assertData(resp.json, state)

    def test_update_invoice_state(self):
        _, state = self.create_invoice_state()

        url = self.item_path(state['name'])
        resp = self.put(url, state)

        self.assertData(resp.json, state)

    def test_delete_invoice_state(self):
        _, state = self.create_invoice_state()

        url = self.item_path(state['name'])
        self.delete(url)

        data = self.central_service.list_invoice_state(self.admin_ctxt)
        self.assertLen(0, data)
