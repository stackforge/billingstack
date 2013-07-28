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
Base classes for API tests.
"""
import pecan.testing

from billingstack.openstack.common import jsonutils as json
from billingstack.openstack.common import log
from billingstack.tests.base import ServiceTestCase


LOG = log.getLogger(__name__)


class APITestMixin(object):
    PATH_PREFIX = None

    path = None

    def item_path(self, *args):
        url = self.path + '/%s'
        return url % args

    def _ensure_slash(self, path):
        if not path.startswith('/'):
            path = '/' + path
        return path

    def make_path(self, path):
        path = self._ensure_slash(path)
        if self.PATH_PREFIX:
            path = self._ensure_slash(self.PATH_PREFIX) + path
        return path

    def _query(self, queries):
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': [],
                        }
        for query in queries:
            for name in ['field', 'op', 'value']:
                query_params['q.%s' % name].append(query.get(name, ''))
        return query_params

    def _params(self, params, queries):
        all_params = {}
        all_params.update(params)
        if queries:
            all_params.update(self._query(queries))
        return all_params

    def get(self, path, headers=None, q=[], status_code=200,
            content_type="application/json", **params):
        path = self.make_path(path)
        all_params = self._params(params, q)

        LOG.debug('GET: %s %r', path, all_params)

        response = self.app.get(
            path,
            params=all_params,
            headers=headers)

        LOG.debug('GOT RESPONSE: %s', response.body)

        self.assertEqual(response.status_code, status_code)

        return response

    def post(self, path, data, headers=None, content_type="application/json",
             q=[], status_code=202):
        path = self.make_path(path)

        LOG.debug('POST: %s %s', path, data)

        content = json.dumps(data)
        response = self.app.post(
            path,
            content,
            content_type=content_type,
            headers=headers)

        LOG.debug('POST RESPONSE: %r' % response.body)

        self.assertEqual(response.status_code, status_code)

        return response

    def put(self, path, data, headers=None, content_type="application/json",
            q=[], status_code=202, **params):
        path = self.make_path(path)

        LOG.debug('PUT: %s %s', path, data)

        content = json.dumps(data)
        response = self.app.put(
            path,
            content,
            content_type=content_type,
            headers=headers)

        LOG.debug('PUT RESPONSE: %r' % response.body)

        self.assertEqual(response.status_code, status_code)

        return response

    def patch_(self, path, data, headers=None, content_type="application/json",
               q=[], status_code=200, **params):
        path = self.make_path(path)

        LOG.debug('PUT: %s %s', path, data)

        content = json.dumps(data)
        response = self.app.patch(
            path,
            content,
            content_type=content_type,
            headers=headers)

        LOG.debug('PATCH RESPONSE: %r', response.body)

        self.assertEqual(response.status_code, status_code)

        return response

    def delete(self, path, status_code=204, headers=None, q=[], **params):
        path = self.make_path(path)
        all_params = self._params(params, q)

        LOG.debug('DELETE: %s %r', path, all_params)

        response = self.app.delete(path, params=all_params)

        self.assertEqual(response.status_code, status_code)

        return response


class FunctionalTest(ServiceTestCase, APITestMixin):
    """
    billingstack.api base test
    """

    def setUp(self):
        super(FunctionalTest, self).setUp()

        # NOTE: Needs to be started after the db schema is created
        self.start_storage('central')
        self.start_service('central')
        self.setSamples()

        self.app = self.make_app()

    def make_app(self):
        self.config = {
            'app': {
                'root': 'billingstack.api.v2.controllers.root.RootController',
                'modules': ['billingstack.api'],
            }
        }
        return pecan.testing.load_test_app(self.config)
