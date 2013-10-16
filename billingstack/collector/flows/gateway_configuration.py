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


ACTION = 'gateway_configuration:create'

LOG = log.getLogger(__name__)


class EntryCreateTask(tasks.RootTask):
    def __init__(self, storage, **kw):
        super(EntryCreateTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, values):
        values['state'] = states.VERIFYING
        return self.storage.create_pg_config(ctxt, values)


class PrerequirementsTask(tasks.RootTask):
    """
    Fetch provider information for use in the next task.
    """
    def __init__(self, storage, **kw):
        super(PrerequirementsTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, gateway_config):
        return self.storage.get_pg_provider(
            ctxt, gateway_config['provider_id'])


class BackendVerifyTask(tasks.RootTask):
    """
    This is the verification task that runs in a threaded flow.

    1. Load the Provider Plugin via entrypoints
    2. Instantiate the Plugin with the Config
    3. Execute verify_config call
    4. Update storage accordingly
    """
    def __init__(self, storage, **kw):
        super(BackendVerifyTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, gateway_config, gateway_provider):
        gateway_provider_cls = get_provider(gateway_provider['name'])
        gateway_provider_obj = gateway_provider_cls(gateway_config)

        try:
            gateway_provider_obj.verify_config()
        except exceptions.ConfigurationError:
            self.storage.update_pg_config(
                ctxt, gateway_config['id'], {'state': states.INVALID})
            raise
        self.storage.update_pg_config(
            ctxt, gateway_config['id'], {'state': states.ACTIVE})


def create_flow(storage):
    flow = linear_flow.Flow(ACTION + ':initial')

    entry_task = EntryCreateTask(
        storage, provides='gateway_config', prefix=ACTION)
    flow.add(entry_task)

    backend_flow = linear_flow.Flow(ACTION + ':backend')
    prereq_task = PrerequirementsTask(
        storage, provides='gateway_provider', prefix=ACTION)
    backend_flow.add(prereq_task)
    backend_flow.add(BackendVerifyTask(storage, prefix=ACTION))

    flow.add(backend_flow)

    return flow
