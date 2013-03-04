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

import logging

from billingstack.tests.api.v1.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestProduct(FunctionalTest):
    __test__ = True
    path = "merchants/%s/products"
   
    def test_product_add(self):
        fixture = self.get_fixture('product')
        
        url = self.path % self.merchant['id']
        resp = self.post(url, fixture)

        self.assertData(fixture, resp.json)

    def test_product_list(self):
        self.product_add(self.merchant['id'])

        url = self.path % self.merchant['id']
        resp = self.get(url)

        self.assertLen(1, resp.json)

    def test_product_get(self):
        _, product = self.product_add(self.merchant['id'])

        url = self.item_path(self.merchant['id'], product['id'])
        resp = self.get(url)

        self.assertData(resp.json, product)

    def test_product_update(self):
        _, product = self.product_add(self.merchant['id'])
        product['name'] = 'test'

        url = self.item_path(self.merchant['id'], product['id'])
        resp = self.put(url, product)

        self.assertData(resp.json, product)

    def test_product_delete(self):
        _, product = self.product_add(self.merchant['id'])

        url = self.item_path(self.merchant['id'], product['id'])
        self.delete(url)

        self.assertLen(0, self.central_service.product_list(self.admin_ctxt))
