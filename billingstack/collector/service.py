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

import sys

from oslo.config import cfg
from taskflow.engines import run as run_flow

from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.openstack.common import service as os_service
from billingstack.storage.utils import get_connection
from billingstack.central.rpcapi import CentralAPI
from billingstack import service as bs_service
from billingstack.collector.flows import (
    gateway_configuration, payment_method)


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

    def start(self):
        self.storage_conn = get_connection('collector')
        super(Service, self).start()

    def wait(self):
        super(Service, self).wait()
        self.conn.consumer_thread.wait()

    # PGP
    def list_pg_providers(self, ctxt, **kw):
        return self.storage_conn.list_pg_providers(ctxt, **kw)

    # PGC
    def create_pg_config(self, ctxt, values):
        flow = gateway_configuration.create_flow(self.storage_conn)
        results = run_flow(flow, store={'values': values, 'ctxt': ctxt})
        return results['gateway_config']

    def list_pg_configs(self, ctxt, **kw):
        return self.storage_conn.list_pg_configs(ctxt, **kw)

    def get_pg_config(self, ctxt, id_):
        return self.storage_conn.get_pg_config(ctxt, id_)

    def update_pg_config(self, ctxt, id_, values):
        return self.storage_conn.update_pg_config(ctxt, id_, values)

    def delete_pg_config(self, ctxt, id_):
        return self.storage_conn.delete_pg_config(ctxt, id_)

    # PM
    def create_payment_method(self, ctxt, values):
        flow = payment_method.create_flow(self.storage_conn)
        results = run_flow(flow, store={'values': values, 'ctxt': ctxt})
        return results['payment_method']

    def list_payment_methods(self, ctxt, **kw):
        return self.storage_conn.list_payment_methods(ctxt, **kw)

    def get_payment_method(self, ctxt, id_, **kw):
        return self.storage_conn.get_payment_method(ctxt, id_)

    def update_payment_method(self, ctxt, id_, values):
        return self.storage_conn.update_payment_method(ctxt, id_, values)

    def delete_payment_method(self, ctxt, id_):
        return self.storage_conn.delete_payment_method(ctxt, id_)


def launch():
    bs_service.prepare_service(sys.argv)
    launcher = os_service.launch(Service(),
                                 cfg.CONF['service:collector'].workers)
    launcher.wait()
