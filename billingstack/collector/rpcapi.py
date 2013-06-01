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


collector_api = CollectorAPI()
