# -*- encoding: utf-8 -*-
#
# Copyright 2013 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in co68mpliance with the License. You may obtain
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

from billingstack import tasks
from billingstack.openstack.common import log

ACTION = 'merchant:create'

LOG = log.getLogger(__name__)


class EntryCreateTask(tasks.RootTask):
    def __init__(self, storage, **kw):
        super(EntryCreateTask, self).__init__(**kw)
        self.storage = storage

    def execute(self, ctxt, values):
        return self.storage.create_merchant(ctxt, values)


def create_flow(storage):
    flow = linear_flow.Flow(ACTION)

    entry_task = EntryCreateTask(storage, provides='merchant', prefix=ACTION)
    flow.add(entry_task)

    return flow
