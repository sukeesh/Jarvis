import requests
from plugin import plugin

# ANSI escape sequences to print in color


class color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    TAIL = '\033[0m'


# List of default crypto pairs
favorite = [
    'BTC/USD',
    'BTC/ETH',
    'BTC/LTC',
    'BTC/XRP'
]
# If the price is down, print in red. If the price is up, print in green


def print_in_color(change):
    if float(change) < 0:
        return color.RED + str(change) + color.TAIL
    else:
        return color.GREEN + str(change) + color.TAIL

# Main function. It requires the base and target
# crypto symbols, e.g. [BTC, XRP]
# to build a URL.


def query(base, target):

    # Bulding a url from base and target currency symbols
    # It must look like this: https://api.cryptonator.com/api/ticker/btc-eth

    url = 'https://api.cryptonator.com/api/ticker/{}-{}'.format(
        base.lower(), target.lower())

    try:
        response = requests.get(url).json()
        price = response['ticker']['price']
        change = response['ticker']['change']

    # This error occurs if the pair is non-existent
    except KeyError:
        print("Wrong pair {}/{}! \nFull list of symbols is here: https://coinmarketcap.com/all/views/all/\n".format(base, target))

    # Results
    else:
        print("\t{}/{}\nPrice: {}\nChange: {} {}\n".format(base, target, price, print_in_color(change), target))


# Iterate over your favorite crypto pairs
@plugin("cryptotracker")
def check_favorites(jarvis, s):
    for pair in favorite:
        base, target = pair.split('/')
        query(base, target)
