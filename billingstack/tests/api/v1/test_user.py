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


class TestUser(FunctionalTest):
    __test__ = True
    path = "merchants/%s"
   
    def test_user_add(self):
        fixture = self.get_fixture('user')

        fixture['password'] = 'test'

        url = self.path % self.merchant['id'] + '/users'
        resp = self.post(url, fixture)

        # The password isn't returned when doing this...
        del fixture['password']

        self.assertData(fixture, resp.json)

    def test_user_list(self):
        self.user_add(self.merchant['id'])

        url = self.path % self.merchant['id'] + '/users'
        resp = self.get(url)

        self.assertLen(1, resp.json)

    def test_user_get(self):
        _, user = self.user_add(self.merchant['id'])

        url = self.path % self.merchant['id'] + '/users/' + user['id']
        resp = self.get(url)

        self.assertData(resp.json, user)

    def test_user_update(self):
        _, user = self.user_add(self.merchant['id'])
        user['name'] = 'test'

        url = self.path % self.merchant['id'] + '/users/' + user['id']
        resp = self.put(url, user)

        self.assertData(resp.json, user)

    def test_user_delete(self):
        _, user = self.user_add(self.merchant['id'])

        url = self.path % self.merchant['id'] + '/users/' + user['id']
        self.delete(url)

        self.assertLen(0, self.central_service.user_list(self.admin_ctxt))