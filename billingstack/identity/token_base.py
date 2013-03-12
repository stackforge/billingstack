import copy
import datetime

from oslo.config import cfg

from billingstack import utils
from billingstack.identity import cms
from billingstack.openstack.common import timeutils
from billingstack.plugin import Plugin


cfg.CONF.register_group(
    cfg.OptGroup(name='identity:token', title="Token configuration"))


cfg.CONF.register_opts([
    cfg.IntOpt('expiration', default=86400)],
    group='identity:token')


def unique_id(token_id):
    """Return a unique ID for a token.

    The returned value is useful as the primary key of a database table,
    memcache store, or other lookup table.

    :returns: Given a PKI token, returns it's hashed value. Otherwise, returns
              the passed-in value (such as a UUID token ID or an existing
              hash).
    """
    return cms.cms_hash_token(token_id)


def default_expire_time():
    """Determine when a fresh token should expire.

    Expiration time varies based on configuration (see ``[token] expiration``).

    :returns: a naive UTC datetime.datetime object

    """
    expiration = cfg.CONF['identity:token'].expiration
    expire_delta = datetime.timedelta(seconds=expiration)
    return timeutils.utcnow() + expire_delta


class TokenPlugin(Plugin):
    __plugin_ns__ = 'billingstack.token'
    __plugin_type__ = 'token'

    """
    Base for Token providers like Memcache, SQL, Redis.....

    Note: This is NOT responsable for user / password authentication. It's a
    layer that manages tokens....
    """
    def get_token(self, token_id):
        """
        Get a Token

        :param token_id: Token ID to get...
        """
        raise NotImplementedError

    def delete_token(self, token_id):
        """
        Delete a Token

        :param token_id: Token ID to delete.
        """
        raise NotImplementedError

    def list_tokens(self):
        """
        List tokens
        """

    def list_revoked(self):
        """
        List out revoked Tokens.
        """
        raise NotImplementedError


