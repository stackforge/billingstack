from billingstack.openstack.common import log
from billingstack.tests.base import TestCase


LOG = log.getLogger(__name__)


class ProviderTestCase(TestCase):
    """
    Common set of tests for the API that all Providers should implement
    """
    __test__ = False

    def setUp(self):
        super(ProviderTestCase, self).setUp()

        info = self.get_fixture('contact_info')
        _, self.customer = self.create_customer(
            self.merchant['id'],
            contact_info=info)

        _, self.provider = self.pg_provider_register()

    def test_create_account(self):
        expected = self.pgp.create_account(self.customer)
        actual = self.pgp.get_account(self.customer['id'])
        self.assertEqual(expected['id'], actual['id'])

    def test_list_accounts(self):
        self.pgp.create_account(self.customer)
        actual = self.pgp.list_accounts()
        self.assertLen(0, actual)

    def test_get_account(self):
        expected = self.pgp.create_account(self.customer)
        actual = self.pgp.get_account(self.customer['id'])
        self.assertEqual(expected['id'], actual['id'])

    def test_delete_account(self):
        data = self.pgp.create_account(self.customer)
        self.pgp.delete_account(data['id'])

    def pm_create(self):
        """
        Create all the necassary things to make a card
        """
        fixture, data = self.create_payment_method(
            self.customer['id'],
            self.provider['methods'][0]['id'])

        self.pgp.create_account(self.customer)
        return fixture, self.pgp.create_payment_method(data)

    def test_create_payment_method(self):
        fixture, pm = self.pm_create()

    def test_list_payment_methods(self):
        fixture, pm = self.pm_create()
        assert len(self.pgp.list_payment_method(self.customer['id'])) == 1

    def test_get_payment_method(self):
        fixture, pm = self.pm_create()
        assert pm == self.pgp.get_payment_method(pm['id'])
