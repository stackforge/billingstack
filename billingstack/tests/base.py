import copy
import os
import shutil
import uuid

import fixtures
import mox
import stubout
import testtools

from oslo.config import cfg
# NOTE: Currently disabled
# from billingstack.openstack.common import policy
from billingstack import exceptions
from billingstack import paths
from billingstack import samples
from billingstack.openstack.common.context import RequestContext, \
    get_admin_context
from billingstack.openstack.common import importutils


cfg.CONF.import_opt(
    'rpc_backend',
    'billingstack.openstack.common.rpc.impl_fake')


CONF = cfg.CONF
CONF.import_opt('host', 'billingstack.netconf')


STORAGE_CACHE = {}


# Config Methods
def set_config(**kwargs):
    group = kwargs.pop('group', None)

    for k, v in kwargs.iteritems():
        cfg.CONF.set_override(k, v, group)


class ConfFixture(fixtures.Fixture):
    """Fixture to manage global conf settings."""

    def __init__(self, conf):
        self.conf = conf

    def setUp(self):
        super(ConfFixture, self).setUp()
        self.conf.set_default('host', 'fake-mini')
        self.conf.set_default('fake_rabbit', True)
        self.conf.set_default('rpc_backend',
                              'billingstack.openstack.common.rpc.impl_fake')
        self.conf.set_default('rpc_cast_timeout', 5)
        self.conf.set_default('rpc_response_timeout', 5)
        self.conf.set_default('verbose', True)
        self.addCleanup(self.conf.reset)


class FixtureHelper(object):
    """Underlying helper object for a StorageFixture to hold driver methods"""

    def __init__(self, fixture):
        """
        :param fixture: The fixture object
        """
        self.fixture = fixture

    def setUp(self):
        """Runs pr test, typically a db reset or similar"""

    def pre_migrate(self):
        """Run before migrations"""

    def migrate(self):
        """Migrate the storage"""

    def post_migrate(self):
        """This is executed after migrations"""

    def post_init(self):
        """Runs at the end of the object initialization"""


class SQLAlchemyHelper(FixtureHelper):
    def __init__(self, fixture):
        super(SQLAlchemyHelper, self).__init__(fixture)

        self.sqlite_db = fixture.kw.get('sqlite_db')
        self.sqlite_clean_db = fixture.kw.get('sqlite_clean_db')
        self.testdb = None

    def setUp(self):
        if self.fixture.database_connection == "sqlite://":
            conn = self.fixture.connection.engine.connect()
            conn.connection.executescript(self._as_string)
            self.fixture.addCleanup(self.fixture.connection.engine.dispose)
        else:
            shutil.copyfile(paths.state_path_rel(self.sqlite_clean_db),
                            paths.state_path_rel(self.sqlite_db))

    def pre_migrate(self):
        self.fixture.connection.engine.dispose()
        self.fixture.connection.engine.connect()
        if self.fixture.database_connection == "sqlite://":
            #https://github.com/openstack/nova/blob/master/nova/test.py#L82-L84
            pass
        else:
            testdb = paths.state_path_rel(self.sqlite_db)
            if os.path.exists(testdb):
                return

    def migrate(self):
        self.fixture.connection.setup_schema()

    def post_init(self):
        if self.fixture.database_connection == "sqlite://":
            conn = self.fixture.connection.engine.connect()
            self._as_string = "".join(
                l for l in conn.connection.iterdump())
            self.fixture.connection.engine.dispose()
        else:
            cleandb = paths.state_path_rel(self.sqlite_clean_db)
            shutil.copyfile(self.testdb, cleandb)


class StorageFixture(fixtures.Fixture):
    """
    Storage fixture that for now just supports SQLAlchemy
    """
    def __init__(self, svc, **kw):
        self.svc = svc
        self.kw = kw

        self.driver = kw.get('storage_driver', 'sqlalchemy')
        self.database_connection = kw.get('database_connection', 'sqlite://')

        self.svc_group = 'service:%s' % self.svc
        self.driver_group = '%s:%s' % (self.svc, self.driver)

        cfg.CONF.import_opt('storage_driver', 'billingstack.%s' % self.svc,
                            group=self.svc_group)
        set_config(storage_driver=self.driver, group=self.svc_group)

        # FIXME: Move this to a generic get_storage() method instead?
        self.module = importutils.import_module(
            'billingstack.%s.storage' % self.svc)

        # FIXME: Workout a way to support the different storage types
        self.helper = SQLAlchemyHelper(self)

        cfg.CONF.import_opt(
            'database_connection',
            'billingstack.%s.storage.impl_%s' % (self.svc, self.driver),
            group=self.driver_group)

        set_config(database_connection=self.database_connection,
                   group=self.driver_group)

        self.connection = self.get_storage_connection(**kw)

        self.helper.pre_migrate()
        self.helper.migrate()
        self.helper.post_migrate()
        self.helper.post_init()

        for hook in kw.get('hooks', []):
            hook()

    def setUp(self):
        super(StorageFixture, self).setUp()
        self.helper.setUp()

    def get_storage_connection(self, **kw):
        """
        Import the storage module for the service that we are going to act on,
        then return a connection object for that storage module.

        :param service: The service.
        """
        engine = self.module.get_engine(self.driver)
        return engine.get_connection()


class ServiceFixture(fixtures.Fixture):
    """Run service as a test fixture, semi-copied from Nova"""

    def __init__(self, name, host=None, **kwargs):
        host = host and host or uuid.uuid4().hex
        kwargs.setdefault('host', host)
        kwargs.setdefault('binary', 'billingstack-%s' % name)
        self.name = name
        self.kwargs = kwargs

        self.cls = self.get_service(self.name)

    @staticmethod
    def get_service(svc):
        """
        Return a service

        :param service: The service.
        """
        return importutils.import_class('billingstack.%s.service.Service' %
                                        svc)

    def setUp(self):
        super(ServiceFixture, self).setUp()
        self.service = self.cls()
        self.service.start()


class MoxStubout(fixtures.Fixture):
    """Deal with code around mox and stubout as a fixture."""

    def setUp(self):
        super(MoxStubout, self).setUp()
        # emulate some of the mox stuff, we can't use the metaclass
        # because it screws with our generators
        self.mox = mox.Mox()
        self.stubs = stubout.StubOutForTesting()
        self.addCleanup(self.stubs.UnsetAll)
        self.addCleanup(self.stubs.SmartUnsetAll)
        self.addCleanup(self.mox.UnsetStubs)
        self.addCleanup(self.mox.VerifyAll)


class AssertMixin(object):
    """
    Mixin to hold assert helpers.

    """
    def assertLen(self, expected_length, obj):
        """
        Assert a length of a object

        :param obj: The object ot run len() on
        :param expected_length: The length in Int that's expected from len(obj)
        """
        self.assertEqual(len(obj), expected_length)

    def assertData(self, expected_data, data):
        """
        A simple helper to very that at least fixture data is the same
        as returned

        :param expected_data: Data that's expected
        :param data: Data to check expected_data against
        """
        for key, value in expected_data.items():
            self.assertEqual(data[key], value)

    def assertDuplicate(self, func, *args, **kw):
        exception = kw.pop('exception', exceptions.Duplicate)
        with testtools.ExpectedException(exception):
            func(*args, **kw)

    def assertMissing(self, func, *args, **kw):
        exception = kw.pop('exception', exceptions.NotFound)
        with testtools.ExpectedException(exception):
            func(*args, **kw)


class BaseTestCase(testtools.TestCase, AssertMixin):
    """
    A base test class to be used for typically non-service kind of things.
    """
    def setUp(self):
        super(BaseTestCase, self).setUp()

        test_timeout = os.environ.get('OS_TEST_TIMEOUT', 0)
        try:
            test_timeout = int(test_timeout)
        except ValueError:
            # If timeout value is invalid do not set a timeout.
            test_timeout = 0
        if test_timeout > 0:
            self.useFixture(fixtures.Timeout(test_timeout, gentle=True))

        if (os.environ.get('OS_STDOUT_CAPTURE') == 'True' or
                os.environ.get('OS_STDOUT_CAPTURE') == '1'):
            stdout = self.useFixture(fixtures.StringStream('stdout')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stdout', stdout))
        if (os.environ.get('OS_STDERR_CAPTURE') == 'True' or
                os.environ.get('OS_STDERR_CAPTURE') == '1'):
            stderr = self.useFixture(fixtures.StringStream('stderr')).stream
            self.useFixture(fixtures.MonkeyPatch('sys.stderr', stderr))

        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self.useFixture(ConfFixture(cfg.CONF))

        mox_fixture = self.useFixture(MoxStubout())
        self.mox = mox_fixture
        self.stubs = mox_fixture.stubs
        self.addCleanup(self._clear_attrs)
        self.useFixture(fixtures.EnvironmentVariable('http_proxy'))
        #self.policy = self.useFixture(policy_fixture.PolicyFixture())

    def _clear_attrs(self):
        # Delete attributes that don't start with _ so they don't pin
        # memory around unnecessarily for the duration of the test
        # suite
        for key in [k for k in self.__dict__.keys() if k[0] != '_']:
            del self.__dict__[key]

    def get_fixture(self, name, fixture=0, values={}):
        """
        Get a fixture from self.samples and override values if necassary
        """
        _values = copy.copy(self.samples[name][fixture])
        _values.update(values)
        return _values


class Services(dict):
    def __getattr__(self, name):
        if name not in self:
            raise AttributeError(name)
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value


class TestCase(BaseTestCase):
    """Base test case for services etc"""
    def setUp(self):
        super(TestCase, self).setUp()

        self.samples = samples.get_samples()
        self.admin_ctxt = self.get_admin_context()

        # NOTE: No services up by default
        self.services = Services()

    def get_admin_context(self):
        return get_admin_context()

    def get_context(self, **kw):
        return RequestContext(**kw)

    def start_service(self, name, host=None, **kwargs):
        fixture = self.useFixture(ServiceFixture(name, host, **kwargs))
        self.services[name] = fixture.service
        return fixture

    def start_storage(self, name, **kw):
        fixture = StorageFixture(name, **kw)
        global STORAGE_CACHE
        if not name in STORAGE_CACHE:
            STORAGE_CACHE[name] = fixture
        self.useFixture(STORAGE_CACHE[name])
        return fixture

    def setSamples(self):
        _, self.currency = self.create_currency()
        _, self.language = self.create_language()
        _, self.merchant = self.create_merchant()

    def _account_defaults(self, values):
        # NOTE: Do defaults
        if not 'currency_name' in values:
            values['currency_name'] = self.currency['name']

        if not 'language_name' in values:
            values['language_name'] = self.language['name']

    def create_language(self, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_currency(self, fixture=0, values={}, **kw):
        raise NotImplementedError

    def crealfte_invoice_state(self, fixture=0, values={}, **kw):
        raise NotImplementedError

    def pg_provider_register(self, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_merchant(self, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_pg_config(self, merchant_id, fixture=0, values={},
                         **kw):
        raise NotImplementedError

    def create_customer(self, merchant_id, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_payment_method(self, customer_id, fixture=0, values={}, **kw):
        raise NotImplementedError

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_product(self, merchant_id, fixture=0, values={}, **kw):
        raise NotImplementedError

    def create_plan(self, merchant_id, fixture=0, values={}, **kw):
        raise NotImplementedError


class ServiceTestCase(TestCase):
    """Testcase with some base methods when running in Service ish mode"""
    def create_language(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_language(ctxt, fixture,
                                                              **kw)

    def create_currency(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_currency(ctxt, fixture,
                                                              **kw)

    def create_invoice_state(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('invoice_state', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_invoice_state(
            ctxt, fixture, **kw)

    def pg_provider_register(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_provider', fixture, values)
        if 'methods' not in fixture:
            fixture['methods'] = [self.get_fixture('pg_method')]
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.services.central.pg_provider_register(ctxt, fixture, **kw)

        return fixture, data

    def create_merchant(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.services.central.create_merchant(
            ctxt, fixture, **kw)

    def create_pg_config(self, merchant_id, fixture=0, values={},
                         **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_pg_config(
            ctxt, merchant_id, fixture, **kw)

    def create_customer(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.services.central.create_customer(
            ctxt, merchant_id, fixture, **kw)

    def create_payment_method(self, customer_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_payment_method(
            ctxt, customer_id, fixture, **kw)

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('user', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.user_add(
            ctxt, merchant_id, fixture, **kw)

    def create_product(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('product', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_product(
            ctxt, merchant_id, fixture, **kw)

    def create_plan(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('plan', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.services.central.create_plan(
            ctxt, merchant_id, fixture, **kw)
