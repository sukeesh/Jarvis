import requests
from colorama import Fore
from plugin import plugin


# List of default crypto pairs
FAVORITES = [
    'BTC/USDT',
    'ETH/USDT',
    'LTC/USDT',
    'XRP/USDT',
    'ADA/USDT',
    'XMR/USDT'
]


def print_in_color(change):
    """
    Prints the price change with color. If the price is down, print in red.
    If the price is up, print in green.

    Parameters
    ----------
    change: str
        The price change.
    """
    if float(change) < 0:
        return Fore.RED + str(change) + '%' + Fore.RESET
    else:
        return Fore.GREEN + '+' + str(change) + '%' + Fore.RESET


def check_prices(base, target):
    """"
    It requires the base and target currency symbols,
    e.g. [btc, usdt], to build the URL and print the price
    and  the price change.

    Parameters
    ----------
    base: str
        The base currency
    target: str
        The target currency
    """

    # build the api request
    url = 'https://api.binance.com/api/v3/ticker/24hr'
    params = {
        "symbol": (base.upper() + target.upper()),
    }

    try:
        response = requests.get(
            url, headers={
                'User-Agent': 'Jarvis'}, params=params).json()

        price = response['askPrice']
        change = response['priceChangePercent']

    # this error occurs if the pair is non-existent
    except KeyError:
        print(
            "{WARNING}Wrong pair {}/{}!{COLOR_RESET} "
            "\nFull list of symbols is here: "
            "https://api.binance.com/api/v3/ticker/price"
            "\nDue to API Changes please use USDT for USD Prices"
            "\n".format(
                base,
                target,
                WARNING=Fore.RED,
                COLOR_RESET=Fore.RESET))

    # results
    else:
        print("\t{}/{}\nPrice: {}\nChange: {}\n".format(base.upper(),
              target.upper(), price, print_in_color(change)))


@plugin("cryptotracker")
def main(jarvis, s):
    """
    Finds the price and the change of the price, for
    a pair of currencies or for the default list of favorite pairs.
    -- Example:
        cryptotracker BTC/USDT
    """

    # for a specific pair of currencies
    if s:
        try:
            base, target = s.split('/')
            check_prices(base, target)
        except ValueError:
            print(
                "{WARNING}Wrong format!{COLOR_RESET} Try "
                "{ADVICE}cryptotracker base_currency/target_currency{COLOR_RESET} OR "
                "{ADVICE}cryptotracker{COLOR_RESET}".format(
                    WARNING=Fore.RED,
                    ADVICE=Fore.BLUE,
                    COLOR_RESET=Fore.RESET))
    # for the default favorite pairs
    else:
        for pair in FAVORITES:
            base, target = pair.split('/')
            check_prices(base, target)
