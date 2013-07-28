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
Test Plans
"""

from billingstack.tests.api.v2 import V2Test


class TestPlan(V2Test):
    __test__ = True
    path = "merchants/%s/plans"

    def test_create_plan(self):
        fixture = self.get_fixture('plan')

        url = self.path % self.merchant['id']

        resp = self.post(url, fixture)

        self.assertData(fixture, resp.json)

    def test_list_plans(self):
        self.create_plan(self.merchant['id'])

        url = self.path % self.merchant['id']
        resp = self.get(url)

        self.assertLen(1, resp.json)

    def test_get_plan(self):
        _, plan = self.create_plan(self.merchant['id'])

        url = self.item_path(self.merchant['id'], plan['id'])
        resp = self.get(url)

        self.assertData(resp.json, plan)

    def test_update_plan(self):
        _, plan = self.create_plan(self.merchant['id'])
        plan['name'] = 'test'

        url = self.item_path(self.merchant['id'], plan['id'])
        resp = self.patch_(url, plan)

        self.assertData(resp.json, plan)

    def test_delete_plan(self):
        _, plan = self.create_plan(self.merchant['id'])

        url = self.item_path(self.merchant['id'], plan['id'])
        self.delete(url)

        self.assertLen(0, self.services.central.list_plans(self.admin_ctxt))
