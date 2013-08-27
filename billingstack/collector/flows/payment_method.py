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
from billingstack import exceptions
from billingstack import tasks
from billingstack.collector import states
from billingstack.openstack.common import log
from billingstack.payment_gateway import get_provider
from billingstack.taskflow.patterns import linear_flow, threaded_flow


ACTION = 'payment_method:create'

LOG = log.getLogger(__name__)


class EntryCreateTask(tasks.RootTask):
    """
    Create the initial entry in the database
    """
    def __init__(self, storage, **kw):
        super(EntryCreateTask, self).__init__(**kw)
        self.requires.update(['payment_method'])
        self.provides.update(['payment_method'])
        self.storage = storage

    def __call__(self, ctxt, payment_method):
        payment_method['state'] = states.PENDING
        values = self.storage.create_payment_method(ctxt, payment_method)
        return {'payment_method': values}


class ThreadStartTask(tasks.RootTask):
    """
    This is the end of the current flow, we'll fire off a new threaded flow
    that does stuff towards the actual Gateway which may include blocking code.

    This fires off a new flow that is threaded / greenthreads?
    """
    def __init__(self, storage, **kw):
        super(ThreadStartTask, self).__init__(**kw)
        self.requires.update(['payment_method'])
        self.storage = storage

    def __call__(self, ctxt, payment_method):
        flow = threaded_flow.Flow(ACTION + ':backend')
        flow.add(tasks.ValuesInjectTask({'payment_method': payment_method}))
        flow.add(PrerequirementsTask(self.storage))
        flow.add(BackendCreateTask(self.storage))
        flow.run(ctxt)


class PrerequirementsTask(tasks.RootTask):
    """
    Task to get the config and the provider from the catalog / database.
    """
    def __init__(self, storage, **kw):
        super(PrerequirementsTask, self).__init__(**kw)
        self.requires.update(['payment_method'])
        self.provides.update([
            'payment_method',
            'gateway_config',
            'gateway_provider'])
        self.storage = storage

    def __call__(self, ctxt, **kw):
        kw['gateway_config'] = self.storage.get_pg_config(
            ctxt, kw['payment_method']['provider_config_id'])

        kw['gateway_provider'] = self.storage.get_pg_provider(
            ctxt, kw['gateway_config']['provider_id'])

        return kw


class BackendCreateTask(tasks.RootTask):
    def __init__(self, storage, **kw):
        super(BackendCreateTask, self).__init__(**kw)
        self.requires.update([
            'payment_method',
            'gateway_config',
            'gateway_provider'])
        self.storage = storage

    def __call__(self, ctxt, payment_method, gateway_config, gateway_provider):
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


def create_flow(storage, payment_method):
    """
    The flow for the service to start
    """
    flow = linear_flow.Flow(ACTION + ':initial')

    flow.add(tasks.ValuesInjectTask(
        {'payment_method': payment_method},
        prefix=ACTION))

    entry_task = EntryCreateTask(storage, prefix=ACTION)
    entry_task_id = flow.add(entry_task)

    flow.add(ThreadStartTask(storage, prefix=ACTION))

    return entry_task_id, tasks._attach_debug_listeners(flow)
