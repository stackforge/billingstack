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
from billingstack.openstack.common.context import get_admin_context
from billingstack.payment_gateway import register_providers
from billingstack.manage.base import ListCommand
from billingstack.manage.database import DatabaseCommand


class ProvidersRegister(DatabaseCommand):
    """
    Register Payment Gateway Providers
    """
    def execute(self, parsed_args):
        context = get_admin_context()
        register_providers(context)


class ProvidersList(DatabaseCommand, ListCommand):
    def execute(self, parsed_args):
        context = get_admin_context()
        conn = self.get_connection('collector')

        data = conn.list_pg_providers(context)

        for p in data:
            keys = ['type', 'name']
            methods = [":".join([m[k] for k in keys]) for m in p['methods']]
            p['methods'] = ", ".join(methods)
        return data
