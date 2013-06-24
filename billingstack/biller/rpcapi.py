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
from oslo.config import cfg

from billingstack.openstack.common.rpc import proxy

rpcapi_opts = [
    cfg.StrOpt('biller_topic', default='biller',
               help='the topic biller nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class BillerAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(BillerAPI, self).__init__(
            topic=cfg.CONF.biller_topic,
            default_version=self.BASE_RPC_VERSION)

    # Invoice States
    def create_invoice_state(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_invoice_state',
                         values=values))

    def list_invoice_states(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice_states',
                         criterion=criterion))

    def get_invoice_state(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice_state', id_=id_))

    def update_invoice_state(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice_state',
                         id_=id_, values=values))

    def delete_invoice_state(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice_state', id_=id_))

    # Invoices
    def create_invoice(self, ctxt, merchant_id, values):
        return self.call(ctxt, self.make_msg('create_invoice',
                         merchant_id=merchant_id, values=values))

    def list_invoices(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoices',
                         criterion=criterion))

    def get_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice', id_=id_))

    def update_invoice(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice', id_=id_,
                         values=values))

    def delete_invoice(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice', id_=id_))

    # Invoice lines
    def create_invoice_line(self, ctxt, invoice_id, values):
        return self.call(ctxt, self.make_msg('create_invoice_line',
                         invoice_id=invoice_id, values=values))

    def list_invoice_lines(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_invoice_lines',
                         criterion=criterion))

    def get_invoice_line(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_invoice_line', id_=id_))

    def update_invoice_line(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_invoice_line', id_=id_,
                         values=values))

    def delete_invoice_line(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_invoice_line', id_=id_))


biller_api = BillerAPI()
