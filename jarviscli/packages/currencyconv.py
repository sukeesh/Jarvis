from forex_python.converter import CurrencyRates
from forex_python.bitcoin import BtcConverter
from decimal import Decimal

# currencyconv converts the given ammount to another currency using fore-python
def currencyconv(self, ammount, fr, to):

    b = BtcConverter(force_decimal=True)
    c = CurrencyRates(force_decimal=True)

    if (to == "BTC"):
        result = b.convert_to_btc(Decimal(ammount), fr)
    elif (fr == "BTC"):
        result = b.convert_btc_to_cur(Decimal(ammount), to)
    else:
        result = c.convert(fr, to, Decimal(ammount))

    print result
    return result

# correct_currency checks if the input the user gave is appropriate
# forex-python can only receive inputs that are in this format
def correct_currency(self, c):
    c = c.upper()  # convert a string from lowercase to uppercase
    currencies = {"EUR": ["EURO"], "AUD": ["AUSTRALIAN DOLLAR"], "BGN": ["BULGARIAN LEV"],
    "BRL": ["BRAZILIAN REAL"], "CAD": ["CANADIAN DOLLAR"], "CHF": ["SWISS FRANC"],
    "CNY": ["YUAN RENMINBI"], "CZK": ["CZECH KORUNA"], "DKK": ["DANISH KRONE"],
    "GBP": ["POUND STERLING"], "HKD": ["HONG KONG DOLLAR"], "HRK": ["CROATIAN KUNA", "KUNA"],
    "HUF": ["FORINT"], "IDR": ["RUPIAH"], "ILS": ["NEW ISRAELI SHEQEL"], "INR": ["INDIAN RUPEE"],
    "ISK": ["ICELAND KRONA"], "JPY": ["YEN", "JAPANESE YEN"], "KRW": ["WON"],
    "MXN": ["MEXICAN PESO"], "MYR": ["MALAYSIAN RINGGIT"], "NOK": ["NORWEGIAN KRONE"],
    "NZD": ["NEW ZEALAND DOLLAR"], "PHP": ["PHILIPPINE PESO"], "PLN": ["ZLOTY"],
    "RON": ["NEW ROMANIAN LEU"], "RUB": ["RUSSIAN RUBLE"], "SEK": ["SWEDISH KRONA"],
    "SGD": ["SINGAPORE DOLLAR"], "THB": ["BAHT"], "TRY" : ["TURKISH LIRA"],
    "USD": ["US DOLLAR"], "ZAR": ["RAND"], "BTC": ["XBT", "BITCOINS"]}

    for key, value in currencies.items():
        if (c != key) and (c not in value):
            correct = "1"
        else:
            return key
    return correct
