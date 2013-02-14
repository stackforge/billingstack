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
"""Base classes for API tests.
"""

import os

from pecan import set_config
from pecan.testing import load_test_app

from billingstack.tests import base


class FunctionalTest(base.TestCase):
    """
    Used for functional tests of Pecan controllers where you need to
    test your literal application and its integration with the
    framework.
    """

    PATH_PREFIX = ''

    def setUp(self):
        super(FunctionalTest, self).setUp()
        self.app = self._make_app()

    def _make_app(self, enable_acl=False):
        # Determine where we are so we can set up paths in the config
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..',
                                                )
                                   )

        self.config = {
            'app': {
                'root': 'billingstack.api.controllers.root.RootController',
                'modules': ['billingstack.api'],
                'static_root': '%s/public' % root_dir,
                'template_path': '%s/billingstack/api/templates' % root_dir,
                'enable_acl': enable_acl,
            },

            'logging': {
                'loggers': {
                    'root': {'level': 'INFO', 'handlers': ['console']},
                    'wsme': {'level': 'INFO', 'handlers': ['console']},
                    'billingstack': {'level': 'DEBUG',
                                   'handlers': ['console'],
                                   },
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'simple'
                    }
                },
                'formatters': {
                    'simple': {
                        'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                                   '[%(threadName)s] %(message)s')
                    }
                },
            },
        }

        return load_test_app(self.config)

    def tearDown(self):
        super(FunctionalTest, self).tearDown()
        set_config({}, overwrite=True)

    def get_json(self, path, expect_errors=False, headers=None,
                 q=[], **params):
        full_path = self.PATH_PREFIX + path
        query_params = {'q.field': [],
                        'q.value': [],
                        'q.op': [],
                        }
        for query in q:
            for name in ['field', 'op', 'value']:
                query_params['q.%s' % name].append(query.get(name, ''))
        all_params = {}
        all_params.update(params)
        if q:
            all_params.update(query_params)
        print 'GET: %s %r' % (full_path, all_params)
        response = self.app.get(full_path,
                                params=all_params,
                                headers=headers,
                                expect_errors=expect_errors)
        if not expect_errors:
            response = response.json
        print 'GOT:', response
        return response
