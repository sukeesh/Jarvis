import unittest
from Jarvis import Jarvis


def get_float_input(prompt, input):
    while True:
        try:
            value = float(input.replace(',', '.'))
            return value
        except ValueError:
            print("Sorry, I didn't understand that.")
            prompt = 'Try again: '
            continue


def get_currency_input(prompt, currencies, input):
    """
    get_currency checks if the input the user gave is valid based on the
    dictionary of find_currencies
    """

    while True:
        c = input.upper()
        if c in currencies:
            return currencies[c]
        elif c == "show help".upper():
            print(', '.join(set(currencies.values())))
            prompt = 'Please enter a valid country or currency: '
            continue
        elif c == "try again".upper():
            prompt = 'Please enter a valid country or currency: '
            continue
        else:
            prompt = 'Type -show help- to see valid currencies '\
                     'or -try again- to continue: '


class CurrencyConvTest(unittest.TestCase):

    def setUp(self):
        self = Jarvis()

    def test_currencyconv(self):
        # the rates between the currencies are changing!
        pass

    def test_get_currency(self):
        # normal case
        self.assertEqual(get_currency_input('Enter a currency',
                                      {'GREECE': 'EUR', 'EURO': 'EUR',
                                       'BITCOINS': 'BTC'}, 'Greece'), 'EUR')

    def test_get_float_int(self):
        # normal case
        print("Testing get_float_int checked")
        self.assertEqual(get_float_input("", '1'), 1)

    def test_get_float_comma(self):
        # change comma with dot
        self.assertEqual(get_float_input('Enter a number: ', '12,6'), 12.6)


if __name__ == '__main__':
    unittest.main()
