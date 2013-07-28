# Copyright 2012 Managed I.T.
#
# Author: Kiall Mac Innes <kiall@managedit.ie>
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
#
# Copied: Moniker

from oslo.config import cfg

from billingstack.openstack.common import local
from billingstack.openstack.common import log as logging
from billingstack.openstack.common.context import RequestContext
from billingstack import wsgi

LOG = logging.getLogger(__name__)


def pipeline_factory(loader, global_conf, **local_conf):
    """
    A paste pipeline replica that keys off of auth_strategy.

    Code nabbed from cinder.
    """
    pipeline = local_conf[cfg.CONF['service:api'].auth_strategy]
    pipeline = pipeline.split()
    filters = [loader.get_filter(n) for n in pipeline[:-1]]
    app = loader.get_app(pipeline[-1])
    filters.reverse()
    for filter in filters:
        app = filter(app)
    return app


class NoAuthContextMiddleware(wsgi.Middleware):
    def merchant_id(self, request):
        parts = [p for p in request.path_info.split('/') if p]
        if parts[0] == 'merchants' and len(parts) >= 2:
            return parts[1]

    def process_request(self, request):
        merchant_id = self.merchant_id(request)

        # NOTE(kiall): This makes the assumption that disabling authentication
        #              means you wish to allow full access to everyone.
        context = RequestContext(is_admin=True, tenant=merchant_id)

        # Store the context where oslo-log exepcts to find it.
        local.store.context = context

        # Attach the context to the request environment
        request.environ['context'] = context
