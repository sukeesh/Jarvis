import unittest
from mock import patch
from Jarvis import Jarvis
from packages.currencyconv import get_currency
from utilities.GeneralUtilities import get_float


class CurrencyConvTest(unittest.TestCase):

    def setUp(self):
        self = Jarvis()

    def test_currencyconv(self):
        # the rates between the currencies are changing!
        pass

    @patch('packages.currencyconv.input', return_value='Greece')
    def test_get_currency(self, get_mock):
        # normal case
        self.assertEqual(get_currency('Enter a currency',
                                      {'GREECE': 'EUR', 'EURO': 'EUR',
                                       'BITCOINS': 'BTC'}), 'EUR')

    @patch('utilities.GeneralUtilities.input', return_value='1')
    def test_get_float_int(self, get_mock):
        # normal case
        print("Testing get_float_int checked")
        self.assertEqual(get_float(""), 1)

    @patch('utilities.GeneralUtilities.input', return_value='12,6')
    def test_get_float_comma(self, geet_mock):
        # change comma with dot
        self.assertEqual(get_float('Enter a number: '), 12.6)


if __name__ == '__main__':
    unittest.main()
