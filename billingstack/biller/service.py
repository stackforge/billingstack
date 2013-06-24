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
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.storage.utils import get_connection


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
