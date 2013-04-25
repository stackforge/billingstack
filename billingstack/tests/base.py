import copy
import unittest2
import mox
from oslo.config import cfg
# NOTE: Currently disabled
# from billingstack.openstack.common import policy
from billingstack import exceptions
from billingstack import samples
from billingstack.central import storage
from billingstack.api import service as api_service
from billingstack.central import service as central_service
from billingstack.openstack.common.context import RequestContext, \
    get_admin_context


cfg.CONF.import_opt('storage_driver', 'billingstack.central',
                    group='service:central')
cfg.CONF.import_opt('database_connection',
                    'billingstack.central.storage.impl_sqlalchemy',
                    group='central:sqlalchemy')


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
        with self.assertRaises(exception):
            func(*args, **kw)

    def assertMissing(self, func, *args, **kw):
        exception = kw.pop('exception', exceptions.NotFound)
        with self.assertRaises(exception):
            func(*args, **kw)


class BaseTestCase(unittest2.TestCase, AssertMixin):
    """
    A base test class.
    """
    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        cfg.CONF.reset()
        self.mox.UnsetStubs()
        self.mox.VerifyAll()
        super(BaseTestCase, self).tearDown()

    # Config Methods
    def config(self, **kwargs):
        group = kwargs.pop('group', None)

        for k, v in kwargs.iteritems():
            cfg.CONF.set_override(k, v, group)

    def get_fixture(self, name, fixture=0, values={}):
        """
        Get a fixture from self.samples and override values if necassary
        """
        _values = copy.copy(self.samples[name][fixture])
        _values.update(values)
        return _values

    def get_admin_context(self):
        return get_admin_context()

    def get_context(self, **kw):
        return RequestContext(**kw)


class TestCase(BaseTestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        self.config(
            rpc_backend='billingstack.openstack.common.rpc.impl_fake',
        )

        self.config(
            storage_driver='sqlalchemy',
            group='service:central'
        )

        self.config(
            database_connection='sqlite://',
            group='central:sqlalchemy'
        )

        self.samples = samples.get_samples()

        storage.setup_schema()

        self.admin_ctxt = self.get_admin_context()

    def tearDown(self):
        # NOTE: Currently disabled
        #policy.reset()
        storage.teardown_schema()
        super(TestCase, self).tearDown()

    def get_storage_driver(self):
        connection = storage.get_connection()
        return connection

    def get_central_service(self):
        return central_service.Service()

    def get_api_service(self):
        return api_service.Service()

    def setSamples(self):
        _, self.currency = self.create_currency()
        _, self.language = self.create_language()
        _, self.merchant = self.create_merchant()

    def create_language(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('language', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_language(ctxt, fixture,
                                                             **kw)

    def create_currency(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('currency', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_currency(ctxt, fixture,
                                                             **kw)

    def create_invoice_state(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('invoice_state', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_invoice_state(
            ctxt, fixture, **kw)

    def pg_provider_register(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('pg_provider', fixture, values)
        if 'methods' not in fixture:
            fixture['methods'] = [self.get_fixture('pg_method')]
        ctxt = kw.pop('context', self.admin_ctxt)

        data = self.central_service.pg_provider_register(ctxt, fixture, **kw)

        return fixture, data

    def _account_defaults(self, values):
        # NOTE: Do defaults
        if not 'currency_name' in values:
            values['currency_name'] = self.currency['name']

        if not 'language_name' in values:
            values['language_name'] = self.language['name']

    def create_merchant(self, fixture=0, values={}, **kw):
        fixture = self.get_fixture('merchant', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)

        self._account_defaults(fixture)

        return fixture, self.central_service.create_merchant(
            ctxt, fixture, **kw)

    def create_pg_config(self, merchant_id, fixture=0, values={},
                         **kw):
        fixture = self.get_fixture('pg_config', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_pg_config(
            ctxt, merchant_id, fixture, **kw)

    def create_customer(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('customer', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        self._account_defaults(fixture)
        return fixture, self.central_service.create_customer(
            ctxt, merchant_id, fixture, **kw)

    def create_payment_method(self, customer_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('payment_method', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_payment_method(
            ctxt, customer_id, fixture, **kw)

    def user_add(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('user', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.user_add(
            ctxt, merchant_id, fixture, **kw)

    def create_product(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('product', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_product(
            ctxt, merchant_id, fixture, **kw)

    def create_plan(self, merchant_id, fixture=0, values={}, **kw):
        fixture = self.get_fixture('plan', fixture, values)
        ctxt = kw.pop('context', self.admin_ctxt)
        return fixture, self.central_service.create_plan(
            ctxt, merchant_id, fixture, **kw)
