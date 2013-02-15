# -*- encoding: utf-8 -*-
#
# Copyright © 2012 New Dream Network, LLC (DreamHost)
#
# Author: Doug Hellmann <doug.hellmann@dreamhost.com>
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
# Coped: Ceilometer
"""Test listing raw events.
"""

import datetime
import logging

from billingstack.openstack.common import cfg

from billingstack.tests.api.v1.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestMerchant(FunctionalTest):
    def test_merchant_add(self):
        fixture = self.get_fixture('merchant')
        self._account_defaults(fixture)

        resp = self.post('merchants', fixture)

        self.assertData(fixture, resp.json)

    def test_merchant_list(self):
        resp = self.get('merchants')
        self.assertLen(1, resp.json)

    def test_merchant_get(self):
        resp = self.get('merchants/' + self.merchant['id'])
        self.assertData(resp.json, self.merchant)

    def test_merchant_update(self):
        fixture = self.merchant.copy()
        fixture['name'] = 'test'

        rest = self.put('merchants/' + self.merchant['id'], fixture)

        self.assertData(rest.json, fixture)

    def test_merchant_delete(self):
        self.delete('merchants/' + self.merchant['id'])
        self.assertLen(0, self.storage_conn.merchant_list())
