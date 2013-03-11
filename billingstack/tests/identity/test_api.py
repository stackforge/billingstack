import os

from pecan import set_config

from oslo.config import cfg

from billingstack.samples import get_samples
from billingstack.identity.base import IdentityPlugin
from billingstack.tests.api.base import PecanTestMixin
from billingstack.tests.base import BaseTestCase


cfg.CONF.import_opt('database_connection',
        'billingstack.identity.impl_sqlalchemy',
        group='identity:sqlalchemy')


ROLE = {
    'name': 'Member'
}


class IdentityAPITest(BaseTestCase, PecanTestMixin):
    PATH_PREFIX = '/v1'

    def setUp(self):
        super(IdentityAPITest, self).setUp()

        self.samples = get_samples()

        self.config(
            database_connection='sqlite://',
            group='identity:sqlalchemy')
        self.plugin = IdentityPlugin.get_plugin(invoke_on_load=True)
        self.plugin.setup_schema()

        self.app = self.make_app()

    def tearDown(self):
        super(IdentityAPITest, self).tearDown()
        #self.plugin.teardown_schema()
        set_config({}, overwrite=True)

    def make_config(self, enable_acl=False):
        # Determine where we are so we can set up paths in the config
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                '..',
                                                '..',
                                                )
                                   )

        return {
            'app': {
                'root': 'billingstack.identity.api.v1.RootController',
                'modules': ['billingstack.identity.api'],
                'static_root': '%s/public' % root_dir,
                'template_path': '%s/api/templates' % root_dir,
                'enable_acl': enable_acl,
            },

            'logging': {
                'loggers': {
                    'root': {'level': 'INFO', 'handlers': ['console']},
                    'wsme': {'level': 'INFO', 'handlers': ['console']},
                    'billingstack': {'level': 'DEBUG',
                                   'handlers': ['console'],
                                   },
                },
                'handlers': {
                    'console': {
                        'level': 'DEBUG',
                        'class': 'logging.StreamHandler',
                        'formatter': 'simple'
                    }
                },
                'formatters': {
                    'simple': {
                        'format': ('%(asctime)s %(levelname)-5.5s [%(name)s]'
                                   '[%(threadName)s] %(message)s')
                    }
                },
            },
        }

    # Accounts
    def test_create_account(self):
        values = self.get_fixture('merchant')
        values['type'] = 'merchant'

        self.post('accounts', values)

    def test_list_accounts(self):
        resp = self.get('accounts')
        self.assertLen(0, resp.json)

    def test_get_account(self):
        values = self.get_fixture('merchant')
        values['type'] = 'merchant'

        resp = self.post('accounts', values)

        resp_actual = self.get('accounts/%s' % resp.json['id'])

        self.assertData(resp.json, resp_actual.json)

    def test_update_account(self):
        values = self.get_fixture('merchant')
        values['type'] = 'merchant'

        resp = self.post('accounts', values)

        expected = dict(resp.json, name='Merchant')

        resp = self.put('accounts/%s' % expected['id'], expected)

        self.assertData(expected, resp.json)

    def test_delete_account(self):
        values = self.get_fixture('merchant')
        values['type'] = 'merchant'

        resp = self.post('accounts', values)

        self.delete('accounts/%s' % resp.json['id'])

        resp = self.get('accounts')
        self.assertLen(0, resp.json)

    def test_create_account(self):
        values = self.get_fixture('merchant')
        values['type'] = 'merchant'

        self.post('accounts', values)

    # Roles
    def test_create_role(self):
        values = ROLE.copy()

        resp = self.post('roles', values)

        assert resp.json['name'] == values['name']
        assert resp.json['id'] != None

    def test_list_roles(self):
        resp = self.get('roles')
        self.assertLen(0, resp.json)

    def test_get_role(self):
        values = ROLE.copy()

        resp = self.post('roles', values)

        resp_actual = self.get('roles/%s' % resp.json['id'])

        self.assertData(resp.json, resp_actual.json)

    def test_update_role(self):
        values = ROLE.copy()

        resp = self.post('roles', values)

        expected = dict(resp.json, name='SuperMember')

        resp = self.put('roles/%s' % expected['id'], expected)

        self.assertData(expected, resp.json)

    def test_delete_role(self):
        values = ROLE.copy()

        resp = self.post('roles', values)

        self.delete('roles/%s' % resp.json['id'])

        resp = self.get('roles')
        self.assertLen(0, resp.json)

    def test_create_user(self):
        values = self.get_fixture('users')

        self.post('users', values)

    def test_list_users(self):
        resp = self.get('users')
        self.assertLen(0, resp.json)

    def test_get_user(self):
        values = self.get_fixture('user')

        resp = self.post('users', values)

        resp_actual = self.get('users/%s' % resp.json['id'])

        self.assertData(resp.json, resp_actual.json)

    def test_update_user(self):
        values = self.get_fixture('user')

        resp = self.post('users', values)

        expected = dict(resp.json, name='test')

        resp = self.put('users/%s' % expected['id'], expected)

        self.assertData(expected, resp.json)

    def test_delete_user(self):
        values = self.get_fixture('user')

        resp = self.post('users', values)

        self.delete('users/%s' % resp.json['id'])

        resp = self.get('users')
        self.assertLen(0, resp.json)

    # Grants
    def test_create_grant(self):
        account_data = self.get_fixture('merchant')
        account_data['type'] = 'merchant'

        account = self.post('accounts', account_data).json

        user_data = self.get_fixture('user')
        user = self.post('users', user_data).json

        role_data = ROLE.copy()
        role = self.post('roles', role_data).json

        url = 'accounts/%s/users/%s/roles/%s' % (
            account['id'], user['id'], role['id'])
        self.put(url, {})

    # Grants
    def test_revoke_grant(self):
        account_data = self.get_fixture('merchant')
        account_data['type'] = 'merchant'

        account = self.post('accounts', account_data).json

        user_data = self.get_fixture('user')
        user = self.post('users', user_data).json

        role_data = ROLE.copy()
        role = self.post('roles', role_data).json

        url = 'accounts/%s/users/%s/roles/%s' % (
            account['id'], user['id'], role['id'])

        self.put(url, {})

        self.delete(url)
