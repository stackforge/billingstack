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
from taskflow.engines import run as run_flow


from billingstack.openstack.common import log as logging
from billingstack.openstack.common.rpc import service as rpc_service
from billingstack.openstack.common import service as os_service
from billingstack.central.flows import merchant
from billingstack.storage.utils import get_connection
from billingstack import service as bs_service


cfg.CONF.import_opt('central_topic', 'billingstack.central.rpcapi')
cfg.CONF.import_opt('host', 'billingstack.netconf')
cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = logging.getLogger(__name__)


class Service(rpc_service.Service):
    def __init__(self, *args, **kwargs):
        kwargs.update(
            host=cfg.CONF.host,
            topic=cfg.CONF.central_topic,
        )

        super(Service, self).__init__(*args, **kwargs)

    def start(self):
        self.storage_conn = get_connection('central')
        super(Service, self).start()

    def wait(self):
        super(Service, self).wait()
        self.conn.consumer_thread.wait()

    # Currency
    def create_currency(self, ctxt, values):
        return self.storage_conn.create_currency(ctxt, values)

    def list_currencies(self, ctxt, **kw):
        return self.storage_conn.list_currencies(ctxt, **kw)

    def get_currency(self, ctxt, id_):
        return self.storage_conn.get_currency(ctxt, id_)

    def update_currency(self, ctxt, id_, values):
        return self.storage_conn.update_currency(ctxt, id_, values)

    def delete_currency(self, ctxt, id_):
        return self.storage_conn.delete_currency(ctxt, id_)

    # Language
    def create_language(self, ctxt, values):
        return self.storage_conn.create_language(ctxt, values)

    def list_languages(self, ctxt, **kw):
        return self.storage_conn.list_languages(ctxt, **kw)

    def get_language(self, ctxt, id_):
        return self.storage_conn.get_language(ctxt, id_)

    def update_language(self, ctxt, id_, values):
        return self.storage_conn.update_language(ctxt, id_, values)

    def delete_language(self, ctxt, id_):
        return self.storage_conn.delete_language(ctxt, id_)

    # Contact Info
    def create_contact_info(self, ctxt, obj, values, cls=None,
                            rel_attr='contact_info'):
        return self.storage_conn.create_contact_info(ctxt, values)

    def get_contact_info(self, ctxt, id_):
        return self.storage_conn.get_contact_info(ctxt, id_)

    def update_contact_info(self, ctxt, id_, values):
        return self.storage_conn.update_contact_info(ctxt, values)

    def delete_contact_info(self, ctxt, id_):
        return self.storage_conn.delete_contact_info(ctxt, id_)

    # PGP
    def list_pg_providers(self, ctxt, **kw):
        return self.storage_conn.list_pg_providers(ctxt, **kw)

    def get_pg_provider(self, ctxt, pgp_id):
        return self.storage_conn.get_pg_provider(ctxt, pgp_id)

    # Merchant
    def create_merchant(self, ctxt, values):
        flow = merchant.create_flow(self.storage_conn)
        result = run_flow(flow, engine_conf="parallel",
                          store={'values': values, 'ctxt': ctxt})
        return result['merchant']

    def list_merchants(self, ctxt, **kw):
        return self.storage_conn.list_merchants(ctxt, **kw)

    def get_merchant(self, ctxt, id_):
        return self.storage_conn.get_merchant(ctxt, id_)

    def update_merchant(self, ctxt, id_, values):
        return self.storage_conn.update_merchant(ctxt, id_, values)

    def delete_merchant(self, ctxt, id_):
        return self.storage_conn.delete_merchant(ctxt, id_)

    # Customer
    def create_customer(self, ctxt, merchant_id, values):
        return self.storage_conn.create_customer(ctxt, merchant_id, values)

    def list_customers(self, ctxt, **kw):
        return self.storage_conn.list_customers(ctxt, **kw)

    def get_customer(self, ctxt, id_):
        return self.storage_conn.get_customer(ctxt, id_)

    def update_customer(self, ctxt, id_, values):
        return self.storage_conn.update_customer(ctxt, id_, values)

    def delete_customer(self, ctxt, id_):
        return self.storage_conn.delete_customer(ctxt, id_)

    # Plans
    def create_plan(self, ctxt, merchant_id, values):
        return self.storage_conn.create_plan(ctxt, merchant_id, values)

    def list_plans(self, ctxt, **kw):
        return self.storage_conn.list_plans(ctxt, **kw)

    def get_plan(self, ctxt, id_):
        return self.storage_conn.get_plan(ctxt, id_)

    def update_plan(self, ctxt, id_, values):
        return self.storage_conn.update_plan(ctxt, id_, values)

    def delete_plan(self, ctxt, id_):
        return self.storage_conn.delete_plan(ctxt, id_)

    def get_plan_by_subscription(self, ctxt, id_):
        return self.storage_conn.get_plan_by_subscription(ctxt, id_)

    # PlanItems
    def create_plan_item(self, ctxt, values):
        return self.storage_conn.create_plan_item(ctxt, values)

    def list_plan_items(self, ctxt, **kw):
        return self.storage_conn.list_plan_items(ctxt, **kw)

    def get_plan_item(self, ctxt, plan_id, product_id):
        return self.storage_conn.get_plan_item(ctxt, plan_id, product_id)

    def update_plan_item(self, ctxt, plan_id, product_id, values):
        return self.storage_conn.update_plan_item(
            ctxt, plan_id, product_id, values)

    def delete_plan_item(self, ctxt, plan_id, product_id):
        return self.storage_conn.delete_plan_item(ctxt, plan_id, product_id)

    # Products
    def create_product(self, ctxt, merchant_id, values):
        return self.storage_conn.create_product(ctxt, merchant_id, values)

    def list_products(self, ctxt, **kw):
        return self.storage_conn.list_products(ctxt, **kw)

    def get_product(self, ctxt, id_):
        return self.storage_conn.get_product(ctxt, id_)

    def update_product(self, ctxt, id_, values):
        return self.storage_conn.update_product(ctxt, id_, values)

    def delete_product(self, ctxt, id_):
        return self.storage_conn.delete_product(ctxt, id_)

    # Subscriptions
    def create_subscription(self, ctxt, values):
        return self.storage_conn.create_subscription(ctxt, values)

    def list_subscriptions(self, ctxt, **kw):
        return self.storage_conn.list_subscriptions(ctxt, **kw)

    def get_subscription(self, ctxt, id_):
        return self.storage_conn.get_subscription(ctxt, id_)

    def update_subscription(self, ctxt, id_, values):
        return self.storage_conn.update_subscription(ctxt, id_, values)

    def delete_subscription(self, ctxt, id_):
        return self.storage_conn.delete_subscription(ctxt, id_)


def launch():
    bs_service.prepare_service(sys.argv)
    launcher = os_service.launch(Service(),
                                 cfg.CONF['service:central'].workers)
    launcher.wait()
