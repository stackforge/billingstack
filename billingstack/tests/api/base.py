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
"""
Base classes for API tests.
"""
from billingstack.api.v1 import factory
from billingstack.api.auth import NoAuthContextMiddleware
from billingstack.openstack.common import jsonutils as json
from billingstack.openstack.common import log
from billingstack.tests.base import TestCase


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
            path = path + self._ensure_slash(self.PATH_PREFIX)
        return path

    def load_content(self, response):
        try:
            response.json = json.loads(response.data)
        except ValueError:
            response.json = None

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

        response = self.client.get(path,
                                   content_type=content_type,
                                   query_string=all_params,
                                   headers=headers)

        LOG.debug('GOT RESPONSE: %s', response.data)

        self.assertEqual(response.status_code, status_code)

        self.load_content(response)

        return response

    def post(self, path, data, headers=None, content_type="application/json",
             q=[], status_code=202):
        path = self.make_path(path)

        LOG.debug('POST: %s %s', path, data)

        content = json.dumps(data)
        response = self.client.post(
            path,
            data=content,
            content_type=content_type,
            headers=headers)

        LOG.debug('POST RESPONSE: %r' % response.data)

        self.assertEqual(response.status_code, status_code)

        self.load_content(response)

        return response

    def put(self, path, data, headers=None, content_type="application/json",
            q=[], status_code=202, **params):
        path = self.make_path(path)

        LOG.debug('PUT: %s %s', path, data)

        content = json.dumps(data)
        response = self.client.put(
            path,
            data=content,
            content_type=content_type,
            headers=headers)

        self.assertEqual(response.status_code, status_code)

        LOG.debug('PUT RESPONSE: %r' % response.data)

        self.load_content(response)

        return response

    def delete(self, path, status_code=204, headers=None, q=[], **params):
        path = self.make_path(path)
        all_params = self._params(params, q)

        LOG.debug('DELETE: %s %r', path, all_params)

        response = self.client.delete(path, query_string=all_params)

        #LOG.debug('DELETE RESPONSE: %r' % response.body)

        self.assertEqual(response.status_code, status_code)

        return response


class FunctionalTest(TestCase, APITestMixin):
    """
    billingstack.api base test
    """
    def setUp(self):
        super(FunctionalTest, self).setUp()

        # NOTE: Needs to be started after the db schema is created
        self.central_service = self.get_central_service()
        self.central_service.start()

        self.setSamples()

        self.app = factory({})
        self.app.wsgi_app = NoAuthContextMiddleware(self.app.wsgi_app)
        self.client = self.app.test_client()

    def tearDown(self):
        self.central_service.stop()
        super(FunctionalTest, self).tearDown()
