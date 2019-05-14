import unittest
from Jarvis import Jarvis
from plugins.currencyconv import Currencyconv

from tests import PluginTest


class CurrencyConvTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(Currencyconv)

    def test_get_currency(self):
        self.queue_input('Greece')
        ret = self.test.get_currency(self.jarvis_api, 'Enter a currency', {'GREECE': 'EUR', 'EURO': 'EUR', 'BITCOINS': 'BTC'})
        self.assertEqual(ret, 'EUR')


if __name__ == '__main__':
    unittest.main()
