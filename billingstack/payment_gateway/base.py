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
from billingstack.plugin import Plugin


class Provider(Plugin):
    __plugin_ns__ = 'billingstack.payment_gateway'
    __plugin_type__ = 'payment_gateway'

    __title__ = ''
    __description__ = ''

    def __init__(self, config):
        self.config = config
        self.client = self.get_client()

    @classmethod
    def methods(cls):
        """
        The methods supported by the Provider
        """
        raise NotImplementedError

    @classmethod
    def properties(cls):
        """
        Some extra data about the Provider if any, will be stored as
        JSON in the DB
        """
        return {}

    @classmethod
    def values(cls):
        return dict(
            name=cls.get_plugin_name(),
            title=cls.__title__,
            description=cls.__description__,
            properties=cls.properties())

    def get_client(self):
        """
        Return a Client
        """
        raise NotImplementedError

    @classmethod
    def create_account(self, values):
        """
        Create a new Account

        :param values: A Customer as dict
        """
        raise NotImplementedError

    def get_account(self, id_):
        """
        List Accounts

        :param id_: Account ID to get
        """
        raise NotImplementedError

    def list_account(self):
        """
        List Accounts
        """
        raise NotImplementedError

    def delete_account(self, id_):
        """
        Delete Account

        :param id_: Account ID to delete
        """
        raise NotImplementedError

    def create_payment_method(self, account_id, values):
        """
        Create a new Credit Card or similar

        :param account_d: The Account ID to add this PM to
        :param values: Values to create the PM from
        """
        raise NotImplementedError

    def get_payment_method(self, id_):
        """
        Get a PaymentMethod

        :param id_: The ID of the PM to get
        """
        raise NotImplementedError

    def list_payment_method(self, account_id):
        """
        List PaymentMethods

        :param account_id: The Account ID to list Pms for
        """
        raise NotImplementedError

    def delete_payment_method(self, id_):
        """
        Delete a PaymentMethod
        """
        raise NotImplementedError

    def transaction_add(self, account, values):
        """
        Create a new Transaction

        :param account: The Account entity to create it on
        :param values: Values to create it with
        """
        raise NotImplementedError

    def transaction_get(self, id_):
        """
        Get a Transaction

        :param id_: The ID of the Transaction
        """
        raise NotImplementedError

    def transaction_list(self):
        """
        List Transactions
        """
        raise NotImplementedError

    def transaction_settle(self, id_):
        """
        Settle a Transaction

        :param id_: The ID of the Transaction
        """
        raise NotImplementedError

    def transaction_void(self, id_):
        """
        Void a Transaction

        :param id_: The ID of the Transaction
        """
        raise NotImplementedError

    def transaction_refund(self, id_):
        """
        Refund a Transaction

        :param id_: The ID of the Transaction
        """
        raise NotImplementedError
