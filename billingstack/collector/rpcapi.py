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
    cfg.StrOpt('collector_topic', default='collector',
               help='the topic collector nodes listen on')
]

cfg.CONF.register_opts(rpcapi_opts)


class CollectorAPI(proxy.RpcProxy):
    BASE_RPC_VERSION = '1.0'

    def __init__(self):
        super(CollectorAPI, self).__init__(
            topic=cfg.CONF.collector_topic,
            default_version=self.BASE_RPC_VERSION)

    # PGP
    def list_pg_providers(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_providers',
                         criterion=criterion))

    def get_pg_provider(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_provider', id_=id_))

    # PGM
    def list_pg_methods(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_methods',
                         criterion=criterion))

    def get_pg_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_method', id_=id_))

    def delete_pg_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_pg_method', id_=id_))

    # PGC
    def create_pg_config(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_pg_config',
                         values=values))

    def list_pg_configs(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_pg_configs',
                         criterion=criterion))

    def get_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_pg_config', id_=id_))

    def update_pg_config(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_pg_config', id_=id_,
                         values=values))

    def delete_pg_config(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_pg_config', id_=id_))

    # PaymentMethod
    def create_payment_method(self, ctxt, values):
        return self.call(ctxt, self.make_msg('create_payment_method',
                         values=values))

    def list_payment_methods(self, ctxt, criterion=None):
        return self.call(ctxt, self.make_msg('list_payment_methods',
                         criterion=criterion))

    def get_payment_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('get_payment_method', id_=id_))

    def update_payment_method(self, ctxt, id_, values):
        return self.call(ctxt, self.make_msg('update_payment_method', id_=id_,
                         values=values))

    def delete_payment_method(self, ctxt, id_):
        return self.call(ctxt, self.make_msg('delete_payment_method', id_=id_))


collector_api = CollectorAPI()
