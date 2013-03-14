import copy
import memcache

from oslo.config import cfg

from billingstack import exceptions
from billingstack.openstack.common.gettextutils import _
from billingstack.identity.token_base import TokenPlugin
from billingstack.identity.token_base import default_expire_time, unique_id
from billingstack.openstack.common import jsonutils
from billingstack import utils


cfg.CONF.register_group(
    cfg.OptGroup(name='token:memcache', title="Memcache"))


cfg.CONF.register_opts([
    cfg.StrOpt('memcache_servers', default='127.0.0.1:11211')],
    group='token:memcache')


class MemcachePlugin(TokenPlugin):
    __plugin_name__ = 'memcache'

    def __init__(self, client=None):
        super(MemcachePlugin, self).__init__()
        self._memcache_client = client

    @property
    def client(self):
        return self._memcache_client or self._get_memcache_client()

    def _get_memcache_client(self):
        servers = cfg.CONF[self.name].memcache_servers.split(';')
        self._memcache_client = memcache.Client(servers, debug=0)
        return self._memcache_client

    def _prefix_token_id(self, token_id):
        return 'token-%s' % token_id.encode('utf-8')

    def _prefix_user_id(self, user_id):
        return 'usertokens-%s' % user_id.encode('utf-8')

    def get_token(self, token_id):
        if token_id is None:
            #FIXME(ekarlso): Better error here?
            raise exceptions.NotFound

        ptk = self._prefix_token_id(token_id)
        token = self.client.get(ptk)

        if token is None:
            #FIXME(ekarlso): Better error here?
            raise exceptions.NotFound

        return token

    def create_token(self, token_id, data):
        data_copy = copy.deepcopy(data)
        ptk = self._prefix_token_id(unique_id(token_id))

        if not data_copy.get('expires'):
            data_copy['expires'] = default_expire_time()

        kwargs = {}

        if data_copy['expires'] is not None:
            expires_ts = utils.unixtime(data_copy['expires'])
            kwargs['time'] = expires_ts

        self.client.set(ptk, data_copy, **kwargs)

        if 'id' in data['user']:
            token_data = jsonutils.dumps(token_id)
            user_id = data['user']['id']
            user_key = self._prefix_user_id(user_id)

            if not self.client.append(user_key, ',%s' % token_data):
                if not self.client.add(user_key, token_data):
                    if not self.client.append(user_key, ',%s' % token_data):
                        msg = _('Unable to add token user list.')
                        raise exceptions.UnexpectedError(msg)
        return copy.deepcopy(data_copy)

    def _add_to_revocation_list(self, data):
        data_json = jsonutils.dumps(data)
        if not self.client.append(self.revocation_key, ',%s' % data_json):
            if not self.client.add(self.revocation_key, data_json):
                if not self.client.append(self.revocation_key,
                                          ',%s' % data_json):
                    msg = _('Unable to add token to revocation list.')
                    raise exceptions.UnexpectedError(msg)

    def delete_token(self, token_id):
        # Test for existence
        data = self.get_token(unique_id(token_id))
        ptk = self._prefix_token_id(unique_id(token_id))
        result = self.client.delete(ptk)
        self._add_to_revocation_list(data)
        return result

    def list_tokens(self, user_id, account_id=None, trust_id=None):
        tokens = []
        user_key = self._prefix_user_id(user_id)
        user_record = self.client.get(user_key) or ""
        token_list = jsonutils.loads('[%s]' % user_record)

        for token_id in token_list:
            ptk = self._prefix_token_id(token_id)
            token_ref = self.client.get(ptk)

            if token_ref:
                if account_id is not None:
                    account = token_ref.get('account')
                    if not account:
                        continue
                    if account.get('id') != account_id:
                        continue

                tokens.append(token_id)
        return tokens

    def list_revoked_tokens(self):
        list_json = self.client.get(self.revocation_key)
        if list_json:
            return jsonutils.loads('[%s]' % list_json)
        return []
