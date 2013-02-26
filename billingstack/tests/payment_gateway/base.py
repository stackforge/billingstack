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
        _, self.customer = self.customer_add(
            self.merchant['id'],
            contact_info=info)

        _, self.provider = self.pg_provider_register()

    def test_account_add(self):
        expected = self.pgp.account_add(self.customer)

    def test_account_list(self):
        expected = self.pgp.account_add(self.customer)
        actual = self.pgp.account_list()

    def test_account_get(self):
        expected = self.pgp.account_add(self.customer)
        actual = self.pgp.account_get(self.customer['id'])

    def test_account_delete(self):
        data = self.pgp.account_add(self.customer)
        self.pgp.account_delete(data['id'])

    def pm_create(self):
        """
        Create all the necassary things to make a card
        """
        fixture, data = self.payment_method_add(
            self.customer['id'],
            self.provider['methods'][0]['id'])

        self.pgp.account_add(self.customer)
        return fixture, self.pgp.payment_method_add(data)

    def test_payment_method_add(self):
        fixture, pm = self.pm_create()

    def test_payment_method_list(self):
        fixture, pm = self.pm_create()
        assert len(self.pgp.payment_method_list(self.customer['id'])) == 1

    def test_payment_method_get(self):
        fixture, pm = self.pm_create()
        assert pm == self.pgp.payment_method_get(pm['id'])
