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
Test Language
"""

import logging

from billingstack.tests.api.v1.base import FunctionalTest

LOG = logging.getLogger(__name__)


class TestLanguage(FunctionalTest):
    __test__ = True
    path = "languages"

    def test_create_language(self):
        fixture = self.get_fixture('language', fixture=1)

        resp = self.post(self.path, fixture)

        self.assertData(fixture, resp.json)

    def test_list_language(self):

        resp = self.get(self.path)

        self.assertLen(1, resp.json)

    def test_get_language(self):
        _, language = self.create_language(fixture=1)

        url = self.item_path(language['name'])
        resp = self.get(url)

        self.assertData(resp.json, language)

    def test_update_language(self):
        _, language = self.create_language(fixture=1)

        url = self.item_path(language['name'])
        resp = self.put(url, language)

        self.assertData(resp.json, language)

    def test_delete_language(self):
        _, language = self.create_language(fixture=1)

        url = self.item_path(language['name'])
        self.delete(url)

        data = self.central_service.list_language(self.admin_ctxt)
        self.assertLen(1, data)
