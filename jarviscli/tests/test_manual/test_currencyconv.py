import unittest
from Jarvis import Jarvis
from packages.currencyconv import currencyconv
from packages.currencyconv import correct_currency

from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal

class CurrencyConvTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()

    def test_currencyconv(self):
        # the rates between the currencies are changing!
        b = BtcConverter(force_decimal=True)
        c = CurrencyRates(force_decimal=True)

        result = float(c.convert('EUR', 'USD', Decimal(10.5)))
        self.assertAlmostEqual(float(currencyconv(self, 10.5, 'EUR', 'USD')), result)
        result = float(b.convert_to_btc(Decimal(1.89), 'USD'))
        self.assertAlmostEqual(float(currencyconv(self, 1.89, 'USD', 'BTC')), result)
        result = float(b.convert_btc_to_cur(Decimal(11.88), 'EUR'))
        self.assertAlmostEqual(float(currencyconv(self, 11.88, 'BTC', 'EUR')), result)

    def test_correct_currency(self):
        self.assertEqual(correct_currency(self, 'euro'), 'EUR')
        self.assertEqual(correct_currency(self, 'EUR'), 'EUR')
        self.assertEqual(correct_currency(self, 'bitcoins'), 'BTC')


if __name__ == '__main__':
    unittest.main()
