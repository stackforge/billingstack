import unittest2


from billingstack import exceptions
from billingstack import utils


class UtilsTests(unittest2.TestCase):
    def test_get_currency(self):
        currency = utils.get_currency('nok')
        expected = {'name': u'nok', 'title': u'Norwegian Krone'}
        self.assertEqual(expected, currency)

    def test_get_language(self):
        lang = utils.get_language('nor')
        expected = {'title': u'Norwegian', 'name': u'nor'}
        self.assertEqual(expected, lang)

    def test_invalid_raises(self):
        with self.assertRaises(exceptions.InvalidObject) as cm:
            utils.get_language('random')
            self.assertEqual(cm.exception.errors, {'terminology': 'random'})
