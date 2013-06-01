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
A service that does calls towards the PGP web endpoint or so
"""

import functools
from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.central.rpcapi import CentralAPI


cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('collector_topic', 'billingstack.collector.rpcapi')
cfg.CONF.import_opt('state_path', 'billingstack.paths')


LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.collector_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

        # Get a storage connection
        self.central_api = CentralAPI()

    def get_pg_provider(self, ctxt, pg_info):
        """
        Work out a PGC config either from pg_info or via ctxt fetching it
        from central.
        Return the appropriate PGP for this info.

        :param ctxt: Request context
        :param pg_info: Payment Gateway Config...
        """

    def create_account(self, ctxt, values, pg_config=None):
        """
        Create an Account on the underlying provider

        :param values: The account values
        """

    def __getattr__(self, name):
        """
        Proxy onto the storage api if there is no local method present..

        For now to avoid to have to write up every method once more here...
        """
        if hasattr(self, name):
            return getattr(self, name)

        f = getattr(self.provider, name)
        if not f:
            raise AttributeError

        @functools.wraps(f)
        def _wrapper(*args, **kw):
            return f(*args, **kw)
        setattr(self, name, _wrapper)
        return _wrapper
