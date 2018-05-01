from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal
import csv
import os

FILE_PATH = os.path.abspath(os.path.dirname(__file__))

# currencyconv converts the given ammount to another currency using fore-python
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
    return result

# find_currency includes if the input the user gave is appropriate
# forex-python can only receive inputs that are in this format

def find_currencies():
    with open(os.path.join(FILE_PATH, "../../data/currencies.csv"), mode='r') as infile:
        reader = csv.reader(infile)
        mydict = {r: row[2] for row in reader for r in row}
    return mydict

def get_currency(prompt, currencies):

    first_time = 1
    while True:
        c = raw_input(prompt).upper()
        if c in currencies:
            return currencies[c]
        elif first_time == 1:
            print("Please enter a valid country or currency!")
            get_help = input("Type 1 to see valid inputs or 2 to continue: ")
            if get_help == 1:
                print(currencies.keys())
            elif get_help == 2:
                continue
        first_time = 0
