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
import flask
from oslo.config import cfg
from stevedore import named
from billingstack.openstack.common import log as logging
from billingstack.api.v1.resources import bp as v1_bp

LOG = logging.getLogger(__name__)


cfg.CONF.register_opts([
    cfg.ListOpt('enabled-extensions-v1', default=[],
                help='Enabled API Extensions'),
], group='service:api')


def factory(global_config, **local_conf):
    app = flask.Flask('billingstack.api.v1')

    app.register_blueprint(v1_bp)

    # TODO(kiall): Ideally, we want to make use of the Plugin class here.
    #              This works for the moment though.
    def _register_blueprint(ext):
        app.register_blueprint(ext.plugin)

    # Add any (enabled) optional extensions
    extensions = cfg.CONF['service:api'].enabled_extensions_v1

    if len(extensions) > 0:
        extmgr = named.NamedExtensionManager('billingstack.api.v1.extensions',
                                             names=extensions)
        extmgr.map(_register_blueprint)

    return app
