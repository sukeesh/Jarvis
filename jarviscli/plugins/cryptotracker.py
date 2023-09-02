import requests
from colorama import Fore
from plugin import plugin


# List of default crypto pairs
FAVORITES = [
    'BTC/USD',
    'ETH/USD',
    'LTC/USD',
    'XRP/USD',
    'ADA/USD'
]





def check_prices(base, target):
    """"
    It requires the base and target currency symbols,
    e.g. [BTC, XRP], to build the URL and print the price.

    Parameters
    ----------
    base: str
        The base currency
    target: str
        The target currency
    """

    # build the api url
    url = 'https://api.api-ninjas.com/v1/cryptoprice?symbol={}{}'.format(
        base.lower(), target.lower())

    try:
        response = requests.get(
            url, headers={'X-Api-Key': 'NtgQxUQ02CDzcA5It1e/0w==25CTvSFoQ2nBBCSm'}).json()
        price = response['price']


    # this error occurs if the pair is non-existent
    except KeyError:
        print(
            "{WARNING}Wrong pair {}/{}!{COLOR_RESET} "
            "\nFull list of symbols is here: "
            "\n".format(
                base,
                target,
                WARNING=Fore.RED,
                COLOR_RESET=Fore.RESET))
        api_url = 'https://api.api-ninjas.com/v1/cryptosymbols'
        response = requests.get(api_url, headers={'X-Api-Key': 'NtgQxUQ02CDzcA5It1e/0w==25CTvSFoQ2nBBCSm'}).json()
        if response['symbols']:
            print("All possible pairs are: ")
            for symbol in response['symbols']:
                print(symbol)
        else:
            print("No symbols found")
        print("Please format the query as 'cryptotracker XXX/XXX'")
    # results
    else:
        print("\t{}/{}\nPrice: {}\n".format(base.upper(),
              target.upper(), price))


@plugin("cryptotracker")
def main(jarvis, s):
    """
    Finds the price for
    a pair of currencies or for the default list of favorite pairs.
    -- Example:
        cryptotracker BTC/USD
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
