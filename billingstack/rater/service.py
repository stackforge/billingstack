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
import sys

from oslo.config import cfg
from billingstack.openstack.common import log as logging
from billingstack.openstack.common import service as os_service
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.storage.utils import get_connection
from billingstack import service as bs_service


cfg.CONF.import_opt('rater_topic', 'billingstack.rater.rpcapi')
cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    """
    The Usage / Rater / Rating service for BillingStack.

    This is a service that will receive events typically from a Mediator like
    like Medjatur or the DUDE from Dreamhost that pushes data to the API which
    casts to this service.
    """
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.rater_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

    def start(self):
        self.storage_conn = get_connection('rater')
        super(Service, self).start()

    def create_usage(self, ctxt, values):
        return self.storage_conn.create_usage(ctxt, values)

    def list_usages(self, ctxt, **kw):
        return self.storage_conn.list_usages(ctxt, **kw)

    def get_usage(self, ctxt, id_):
        return self.storage_conn.get_usage(ctxt, id_)

    def update_usage(self, ctxt, id_, values):
        return self.storage_conn.update_usage(ctxt, id_, values)

    def delete_usage(self, ctxt, id_):
        return self.storage_conn.delete_usage(ctxt, id_)


def launch():
    bs_service.prepare_service(sys.argv)
    launcher = os_service.launch(Service(),
                                 cfg.CONF['service:rater'].workers)
    launcher.wait()
