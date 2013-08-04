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
from stevedore.extension import ExtensionManager

from billingstack import exceptions
from billingstack.openstack.common import log
from billingstack.payment_gateway.base import Provider
from billingstack.storage.utils import get_connection


LOG = log.getLogger(__name__)


def _register(ep, context, conn):
    provider = ep.plugin

    values = provider.values()

    LOG.debug("Attempting registration of PGP %s" %
              ep.plugin.get_plugin_name())
    try:
        methods = provider.methods()
    except NotImplementedError:
        msg = "PaymentGatewayProvider %s doesn't provide any methods - Skipped"
        LOG.warn(msg, provider.get_plugin_name())
        return
    values['methods'] = methods
    try:
        conn.pg_provider_register(context, values)
    except exceptions.ConfigurationError:
        return

    LOG.debug("Registered PGP %s with methods %s", values, methods)


def register_providers(context):
    conn = get_connection('collector')
    em = ExtensionManager(Provider.__plugin_ns__)
    em.map(_register, context, conn)


def get_provider(name):
    return Provider.get_plugin(name)
