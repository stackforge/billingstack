# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
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
from taskflow.patterns import linear_flow

from billingstack import exceptions
from billingstack import tasks
from billingstack.collector import states
from billingstack.openstack.common import log
from billingstack.payment_gateway import get_provider


ACTION = 'payment_method:create'

LOG = log.getLogger(__name__)


class EntryCreateTask(tasks.RootTask):
    """
    Create the initial entry in the database
    """
    def __init__(self, storage, **kw):
        super(EntryCreateTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, values):
        values['state'] = states.PENDING
        return self.storage.create_payment_method(ctxt, values)


class PrerequirementsTask(tasks.RootTask):
    """
    Task to get the config and the provider from the catalog / database.
    """
    def __init__(self, storage, **kw):
        super(PrerequirementsTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, values):
        data = {}
        data['gateway_config'] = self.storage.get_pg_config(
            ctxt, values['provider_config_id'])
        data['gateway_provider'] = self.storage.get_pg_provider(
            ctxt, data['gateway_config']['provider_id'])
        return data


class BackendCreateTask(tasks.RootTask):
    def __init__(self, storage, **kw):
        super(BackendCreateTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, payment_method, gateway_config, gateway_provider):
        gateway_provider_cls = get_provider(gateway_provider['name'])
        gateway_provider_obj = gateway_provider_cls(gateway_config)

        try:
            gateway_provider_obj.create_payment_method(
                payment_method['customer_id'],
                payment_method)
        except exceptions.BadRequest:
            self.storage.update_payment_method(
                ctxt, payment_method['id'], {'status': states.INVALID})
            raise


def create_flow(storage):
    """
    The flow for the service to start
    """
    flow = linear_flow.Flow(ACTION + ':initial')

    entry_task = EntryCreateTask(storage, provides='payment_method',
                                 prefix=ACTION)
    flow.add(entry_task)

    backend_flow = linear_flow.Flow(ACTION + ':backend')
    prereq_task = PrerequirementsTask(
        storage,
        provides=set([
            'gateway_config',
            'gateway_provider']),
        prefix=ACTION)
    backend_flow.add(prereq_task)
    backend_flow.add(BackendCreateTask(storage, prefix=ACTION))

    flow.add(backend_flow)

    return flow
