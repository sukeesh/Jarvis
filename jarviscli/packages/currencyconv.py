from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal
from six.moves import input
import csv
import os

FILE_PATH = os.path.abspath(os.path.dirname(__file__))


'''''
 currencyconv converts the given amount to another currency using fore-python
'''''


def currencyconv(self, amount, fr, to):

    b = BtcConverter(force_decimal=True)
    c = CurrencyRates(force_decimal=True)

    if (to == "BTC"):
        result = b.convert_to_btc(Decimal(amount), fr)
    elif (fr == "BTC"):
        result = b.convert_btc_to_cur(Decimal(amount), to)
    else:
        result = c.convert(fr, to, Decimal(amount))

    print result


'''''
find_currency creates a dict with the inputs that
forex-python accepts
'''''


def find_currencies():
    with open(os.path.join(FILE_PATH, "../data/currencies.csv"), mode='r') \
    as infile:
        reader = csv.reader(infile)
        mydict = {r.upper(): row[2] for row in reader for r in row[0:3]}
    return mydict


'''''
get_currency checks if the input the user gave is valid based on the
dictionary of find_currencies
'''''


def get_currency(prompt, currencies):

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
            prompt = 'Type -show help- to see valid currencies ' + \
            'or -try again- to continue: '
