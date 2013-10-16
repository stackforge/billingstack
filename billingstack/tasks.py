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
from taskflow import task

from billingstack.openstack.common import log
from billingstack.openstack.common.gettextutils import _


LOG = log.getLogger(__name__)


def _make_task_name(cls, prefix=None, addons=None):
    prefix = prefix or 'default'
    components = [cls.__module__, cls.__name__]
    if addons:
        for a in addons:
            components.append(str(a))
    return "%s:%s" % (prefix, ".".join(components))


def _attach_debug_listeners(flow):
    """Sets up a nice set of debug listeners for the flow.

    These listeners will log when tasks/flows are transitioning from state to
    state so that said states can be seen in the debug log output which is very
    useful for figuring out where problems are occuring.
    """

    def flow_log_change(state, details):
        LOG.debug(_("%(flow)s has moved into state %(state)s from state"
                    " %(old_state)s") % {'state': state,
                                         'old_state': details.get('old_state'),
                                         'flow': details['flow']})

    def task_log_change(state, details):
        LOG.debug(_("%(flow)s has moved %(runner)s into state %(state)s with"
                    " result: %(result)s") % {'state': state,
                                              'flow': details['flow'],
                                              'runner': details['runner'],
                                              'result': details.get('result')})

    # Register * for all state changes (and not selective state changes to be
    # called upon) since all the changes is more useful.
    flow.notifier.register('*', flow_log_change)
    flow.task_notifier.register('*', task_log_change)
    return flow


class RootTask(task.Task):
    def __init__(self, name=None, prefix=None, addons=None, **kw):
        name = name or _make_task_name(self.__class__, prefix=prefix,
                                       addons=addons)
        super(RootTask, self).__init__(name, **kw)
