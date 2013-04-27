from billingstack.central.storage import get_connection
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

    def get_connection(self):
        """
        Helper to get a storage conncection in BS
        """
        return get_connection()

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
