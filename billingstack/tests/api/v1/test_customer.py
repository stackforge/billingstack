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


class TestCustomer(FunctionalTest):
    path = "merchants/%s/customers"

    def test_customer_add(self):
        fixture = self.get_fixture('customer')
        self._account_defaults(fixture)

        resp = self.post(self.url % self.merchant['id'], fixture)

        self.assertData(fixture, resp.json)

    def test_customer_list(self):
        self.customer_add(self.merchant['id'])
        resp = self.get(self.url % self.merchant['id'])
        self.assertLen(1, resp.json)

    def test_customer_get(self):
        resp = self.get(self.url % self.merchant['id'])
        self.assertData(resp.json, self.customer)

    def test_customer_update(self):
        _, customer = self.customer_add()
        customer['name'] = 'test'

        rest = self.put(self.url + '/%s' % (self.merchant['id'], customer),
                        customer)

        self.assertData(rest.json, customer)

    def test_customer_delete(self):
        _, customer = self.customer_add()
        self.delete(self.path + '/%s' % (self.merchant['id'], customer['id']))
        self.assertLen(0, self.storage_conn.customer_list(self.merchant['id']))