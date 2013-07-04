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


cfg.CONF.import_opt('biller_topic', 'billingstack.biller.rpcapi')
cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    """
    Biller service
    """
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.biller_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

    def start(self):
        self.storage_conn = get_connection('biller')
        super(Service, self).start()

    def wait(self):
        super(Service, self).wait()
        self.conn.consumer_thread.wait()

    def create_invoice_state(self, ctxt, values):
        return self.storage_conn.create_invoice_state(ctxt, values)

    def list_invoice_states(self, ctxt, **kw):
        return self.storage_conn.list_invoice_states(ctxt, **kw)

    def get_invoice_state(self, ctxt, id_):
        return self.storage_conn.get_invoice_state(ctxt, id_)

    def update_invoice_state(self, ctxt, id_, values):
        return self.storage_conn.update_invoice_state(ctxt, id_, values)

    def delete_invoice_state(self, ctxt, id_):
        return self.storage_conn.delete_invoice_state(ctxt, id_)

    def create_invoice(self, ctxt, merchant_id, values):
        return self.storage_conn.create_invoice_state(
            ctxt, merchant_id, values)

    def list_invoices(self, ctxt, **kw):
        return self.storage_conn.list_invoices(ctxt, **kw)

    def get_invoice(self, ctxt, id_):
        return self.storage_conn.get_invoice(ctxt, id_)

    def update_invoice(self, ctxt, id_, values):
        return self.storage_conn.update_invoice(ctxt, id_, values)

    def delete_invoice(self, ctxt, id_):
        return self.storage_conn.delete_invoice(ctxt, id_)

    def create_invoice_line(self, ctxt, invoice_id, values):
        return self.storage_conn.create_invoice_line_state(
            ctxt, invoice_id, values)

    def list_invoice_lines(self, ctxt, **kw):
        return self.storage_conn.list_invoice_lines(ctxt, **kw)

    def get_invoice_line(self, ctxt, id_):
        return self.storage_conn.get_invoice_line(ctxt, id_)

    def update_invoice_line(self, ctxt, id_, values):
        return self.storage_conn.update_invoice_line(ctxt, id_, values)

    def delete_invoice_line(self, ctxt, id_):
        return self.storage_conn.delete_invoice_line(ctxt, id_)


def launch():
    bs_service.prepare_service(sys.argv)
    launcher = os_service.launch(Service(),
                                 cfg.CONF['service:biller'].workers)
    launcher.wait()
