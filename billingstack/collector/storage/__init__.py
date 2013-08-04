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
from billingstack.storage import base


class StorageEngine(base.StorageEngine):
    """Base class for the collector storage"""
    __plugin_ns__ = 'billingstack.collector.storage'


class Connection(base.Connection):
    """Define the base API for collector storage"""
    def pg_provider_register(self):
        """
        Register a Provider and it's Methods
        """
        raise NotImplementedError

    def list_pg_providers(self, ctxt, **kw):
        """
        List available PG Providers
        """
        raise NotImplementedError

    def get_pg_provider(self, ctxt, id_):
        """
        Get a PaymentGateway Provider
        """
        raise NotImplementedError

    def pg_provider_deregister(self, ctxt, id_):
        """
        De-register a PaymentGateway Provider (Plugin) and all it's methods
        """
        raise NotImplementedError

    def create_pg_config(self, ctxt, values):
        """
        Create a PaymentGateway Configuration
        """
        raise NotImplementedError

    def list_pg_configs(self, ctxt, **kw):
        """
        List PaymentGateway Configurations
        """
        raise NotImplementedError

    def get_pg_config(self, ctxt, id_):
        """
        Get a PaymentGateway Configuration
        """
        raise NotImplementedError

    def update_pg_config(self, ctxt, id_, values):
        """
        Update a PaymentGateway Configuration
        """
        raise NotImplementedError

    def delete_pg_config(self, ctxt, id_):
        """
        Delete a PaymentGateway Configuration
        """
        raise NotImplementedError

    def create_payment_method(self, ctxt, values):
        """
        Configure a PaymentMethod like a CreditCard
        """
        raise NotImplementedError

    def list_payment_methods(self, ctxt, criterion=None, **kw):
        """
        List a Customer's PaymentMethods
        """
        raise NotImplementedError

    def get_payment_method(self, ctxt, id_, **kw):
        """
        Get a Customer's PaymentMethod
        """
        raise NotImplementedError

    def update_payment_method(self, ctxt, id_, values):
        """
        Update a Customer's PaymentMethod
        """
        raise NotImplementedError

    def delete_payment_method(self, ctxt, id_):
        """
        Delete a Customer's PaymentMethod
        """
        raise NotImplementedError
