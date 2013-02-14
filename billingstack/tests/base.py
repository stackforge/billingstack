import copy
import unittest2
import mox
from billingstack.openstack.common import cfg
# NOTE: Currently disabled
# from billingstack.openstack.common import policy
from billingstack.openstack.common import log as logging
from billingstack import samples
from billingstack import storage
from billingstack import exceptions


cfg.CONF.import_opt('storage_driver', 'billingstack.api',
                    group='service:api')
cfg.CONF.import_opt('database_connection',
                    'billingstack.storage.impl_sqlalchemy',
                    group='storage:sqlalchemy')


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


class TestCase(unittest2.TestCase, AssertMixin):
    def setUp(self):
        super(TestCase, self).setUp()

        self.mox = mox.Mox()

        self.config(
            storage_driver='sqlalchemy',
            group='service:api'
        )

        self.config(
            database_connection='sqlite://',
            group='storage:sqlalchemy'
        )

        self.samples = samples.get_samples()

        storage.setup_schema()

    def tearDown(self):
        # NOTE: Currently disabled
        #policy.reset()
        storage.teardown_schema()
        cfg.CONF.reset()
        self.mox.UnsetStubs()
        self.mox.VerifyAll()
        super(TestCase, self).tearDown()

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
