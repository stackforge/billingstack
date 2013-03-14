# -*- encoding: utf-8 -*-
#
# Copyright © 2013 Woorea Solutions, S.L
#
# Author: Luis Gervaso <luis@woorea.es>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from oslo.config import cfg

API_SERVICE_OPTS = [
    cfg.IntOpt('api_port', default=9091,
               help='The port for the billing API server'),
    cfg.IntOpt('api_listen', default='0.0.0.0', help='Bind to address'),
    cfg.StrOpt('storage_driver', default='sqlalchemy',
               help='Storage driver to use'),
]

cfg.CONF.register_opts(API_SERVICE_OPTS, 'service:api')
