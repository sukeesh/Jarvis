import unittest
from mock import patch

from Jarvis import Jarvis
from packages.currencyconv import currencyconv
from packages.currencyconv import get_currency
from packages.currencyconv import find_currencies
from utilities.GeneralUtilities import get_float

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal


class CurrencyConvTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()

    def test_currencyconv(self):
        # the rates between the currencies are changing!
        pass

    def test_get_currency(self):
         with patch('packages.currencyconv.get_currency', \
         side_effect='Greece'):
            self.assertEqual(get_currency('Enter a currency', \
            {'GREECE': 'EUR', 'EURO': 'EUR', 'BITCOINS': 'BTC'}), 'EUR')

    @patch('utilities.GeneralUtilities.get_float.input')
    def test_get_float_int(self, mock_input):
        mock_input.return_value='1'
        self.assertEqual(get_float('Enter a number: '), 1)

    @patch('utilities.GeneralUtilities.get_float.input')
    def test_get_float_comma(self, mock_input):
        mock_input.return_value='12,6'
        self.assertEqual(get_float('Enter a number: '), 12.6)

    @patch('utilities.GeneralUtilities.get_float.input')
    def test_get_float_string(self, mock_input):
        mock_input.return_value='hi'
        with self.assertRaises(ValueError):
            get_float('Enter a number: ')


if __name__ == '__main__':
    unittest.main()
