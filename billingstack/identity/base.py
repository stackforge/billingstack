from oslo.config import cfg

from billingstack.plugin import Plugin

cfg.CONF.import_opt('storage_driver', 'billingstack.identity.api',
                    group='service:identity_api')


class IdentityPlugin(Plugin):
    """
    A base IdentityPlugin
    """
    __plugin_ns__ = 'billingstack.identity_plugin'
    __plugin_type__ = 'identity'

    @classmethod
    def get_plugin(self, name=cfg.CONF['service:identity_api'].storage_driver,
                   **kw):
        return super(IdentityPlugin, self).get_plugin(name, **kw)

    def authenticate(self, context, user_id=None, password=None, account_id=None):
        """
        Authenticate a User

        :param user_id: User ID
        :param password: User Password
        :param account_id: User ID
        """
        raise NotImplementedError

    def create_user(self, context, values):
        """
        Create a User.

        :param values: The values to create the User from.
        """
        raise NotImplementedError

    def list_users(self, context, criterion=None):
        """
        List users.

        :param criterion: Criterion to filter on.
        """
        raise NotImplementedError

    def get_user(self, context, id_):
        """
        Get a User by ID.

        :param id_: User id.
        """
        raise NotImplementedError

    def update_user(self, context, id, values):
        """
        Update a User.

        :param id_: User ID.
        :param values: Values to update the User with.
        """
        raise NotImplementedError

    def delete_user(self, context, id_):
        """
        Delete User.

        :param id_: User ID to delete.
        """
        raise NotImplementedError

    def create_account(self, context, values):
        """
        Create an Account.

        :param values: Values to create Account from.
        """
        raise NotImplementedError

    def list_accounts(self, context, criterion=None):
        """
        List Accounts.

        :param criterion: Criterion to filter on.
        """
        raise NotImplementedError

    def get_account(self, context, id_):
        """
        Get Account

        :param id_: Account ID.
        """
        raise NotImplementedError

    def update_account(self, context, id_, values):
        """
        Update Account.

        :param id_: Account ID.
        :param values: Account values.
        """
        raise NotImplementedError

    def delete_account(self, context, id_):
        """
        Delete Account.

        :param id_: Account ID
        """
        raise NotImplementedError

    def create_role(self, context, values):
        """
        Create an Role.

        :param values: Values to create Role from.
        """
        raise NotImplementedError

    def list_roles(self, context, criterion=None):
        """
        List Accounts.

        :param criterion: Criterion to filter on.
        """
        raise NotImplementedError

    def get_role(self, context, id_):
        """
        Get Role.

        :param id_: Role ID.
        """
        raise NotImplementedError

    def update_role(self, context, id_, values):
        """
        Update Role.

        :param id_: Role ID.
        :param values: Role values.
        """
        raise NotImplementedError

    def delete_role(self, context, id_):
        """
        Delete Role.

        :param id_: Role ID
        """
        raise NotImplementedError

    def create_grant(self, context, user_id, account_id, role_id):
        """
        Create a Grant

        :param user_id: User ID.
        :param account_id: Account ID.
        :param role_id: Role ID.
        """
        raise NotImplementedError

    def remove_grant(self, context, user_id, account_id, role_id):
        """
        Remove a Users Role grant on a Account

        :param user_id: User ID.
        :param account_id: Account ID.
        :param role_id: Role ID.
        """
        raise NotImplementedError
