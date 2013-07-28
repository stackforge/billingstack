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
import logging
import os
import pecan
from oslo.config import cfg
from wsgiref import simple_server

from billingstack import service
from billingstack.api import hooks
from billingstack.openstack.common import log

cfg.CONF.import_opt('state_path', 'billingstack.paths')

LOG = log.getLogger(__name__)


def get_config():
    conf = {
        'app': {
            'root': 'billingstack.api.v2.controllers.root.RootController',
            'modules': ['designate.api.v2'],
        }
    }
    return pecan.configuration.conf_from_dict(conf)


def setup_app(pecan_config=None, extra_hooks=None):
    app_hooks = [
        hooks.NoAuthHook()
    ]

    if extra_hooks:
        app_hooks.extend(extra_hooks)

    pecan_config = pecan_config or get_config()

    pecan.configuration.set_config(dict(pecan_config), overwrite=True)

    app = pecan.make_app(
        pecan_config.app.root,
        debug=cfg.CONF.debug,
        hooks=app_hooks,
        force_canonical=getattr(pecan_config.app, 'force_canonical', True)
    )

    return app


class VersionSelectorApplication(object):
    def __init__(self):
        self.v2 = setup_app()

    def __call__(self, environ, start_response):
        return self.v2(environ, start_response)


def start():
    service.prepare_service()

    root = VersionSelectorApplication()

    host = cfg.CONF['service:api'].api_listen
    port = cfg.CONF['service:api'].api_port

    srv = simple_server.make_server(host, port, root)

    LOG.info('Starting server in PID %s' % os.getpid())
    LOG.info("Configuration:")
    cfg.CONF.log_opt_values(LOG, logging.INFO)

    if host == '0.0.0.0':
        LOG.info('serving on 0.0.0.0:%s, view at http://127.0.0.1:%s' %
                 (port, port))
    else:
        LOG.info("serving on http://%s:%s" % (host, port))

    srv.serve_forever()
