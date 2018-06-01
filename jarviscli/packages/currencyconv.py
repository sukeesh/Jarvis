from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal
from six.moves import input
import csv
import os
from utilities.GeneralUtilities import print_say


FILE_PATH = os.path.abspath(os.path.dirname(__file__))


def currencyconv(self, amount, fr, to):
    """
    currencyconv converts the given amount to another currency
    using fore-python
    """

    b = BtcConverter(force_decimal=True)
    c = CurrencyRates(force_decimal=True)

    if (to == "BTC"):
        result = b.convert_to_btc(Decimal(amount), fr)
    elif (fr == "BTC"):
        result = b.convert_btc_to_cur(Decimal(amount), to)
    else:
        result = c.convert(fr, to, Decimal(amount))

    print_say(str(result), self)


def find_currencies():
    """
    find_currency creates a dict with the inputs that forex-python accepts
    """

    with open(os.path.join(FILE_PATH, "../data/currencies.csv"),
              mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {r.upper(): row[2] for row in reader for r in row[0:3]}
    return mydict


def get_currency(prompt, currencies):
    """
    get_currency checks if the input the user gave is valid based
    on the dictionary of find_currencies
    """

    while True:
        c = input(prompt).upper()
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
