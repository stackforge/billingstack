from billingstack.storage import get_connection
from billingstack.plugin import Plugin


class Provider(Plugin):
    __plugin_ns__ = 'billingstack.payment_gateway'
    __plugin_type__ = 'payment_gateway'

    __title__ = ''
    __description__ = ''

    def __init__(self, config):
        self.config = config
        self.client = self.get_client()

    def methods(cls):
        """
        The methods supported by the Provider
        """
        raise NotImplementedError

    @classmethod
    def data(cls):
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
            data=cls.data())

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
    def account_create(self, values):
        """
        Create a new Account
        """
        raise NotImplementedError

    def account_get(self, *args, **kw):
        """
        List Accounts
        """
        raise NotImplementedError

    def account_list(self, *args, **kw):
        """
        List Accounts
        """
        raise NotImplementedError

    def account_delete(self, *args, **kw):
        """
        Delete Account
        """
        raise NotImplementedError

    def payment_method_create(self, account, values):
        """
        Create a new Credit Card or similar

        :param account: The Account entity to create it on
        :param values: Values to create it with
        """
        raise NotImplementedError

    def payment_method_get(self, *args, **kw):
        """
        Get a PaymentMethod
        """
        raise NotImplementedError

    def payment_method_list(self, *args, **kw):
        """
        List PaymentMethods
        """
        raise NotImplementedError

    def payment_method_delete(self, *args, **kw):
        """
        Delete a PaymentMethod
        """
        raise NotImplementedError

    def transaction_create(self, account, values):
        """
        Create a new Transaction

        :param account: The Account entity to create it on
        :param values: Values to create it with
        """
        raise NotImplementedError

    def transaction_get(self, *args, **kw):
        """
        Get a Transaction
        """
        raise NotImplementedError

    def transaction_list(self, *args, **kw):
        """
        List Transactions
        """
        raise NotImplementedError

    def transaction_delete(self, *args, **kw):
        """
        Delete Transaction
        """
        raise NotImplementedError

    def transaction_settle(self, *args, **kw):
        """
        Settle a Transaction
        """
        raise NotImplementedError

    def transaction_void(self, *args, **kw):
        """
        Void a Transaction
        """
        raise NotImplementedError

    def transaction_refund(self, *args, **kw):
        """
        Refund a Transaction
        """
        raise NotImplementedError
