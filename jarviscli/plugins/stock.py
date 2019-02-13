import requests
from plugin import plugin
from colorama import Fore
import re


@plugin('stock')
class Stock:

    def __call__(self, jarvis, s):
        if not s:
            self.usage(jarvis)
        else:
            ps = s.split()
            if ps[0] == 'getid':
                ps.pop(0)
                if ps:
                    name = ' '.join(ps)
                else:
                    name = jarvis.input("Enter the name of the stock to search the ID: ")
                self.get_stock_id(jarvis, name)
            elif ps[0] == 'help':
                self.usage(jarvis)
            # anything else is treated as a stock symbol
            else:
                self.get_stock_data(s)

    @staticmethod
    def get_stock_data(quote):

        resp = requests.get(
            'https://api.iextrading.com/1.0/stock/'
            + quote
            + '/quote')

        if resp.status_code == 200:
            resp = resp.json()
            print("Price: " + str(resp['iexRealtimePrice']))
            print("Open: " + str(resp['open']))
            print("Close: " + str(resp['close']))
            print("Change: " + str(resp['changePercent']) + "%")
            print("MarketCap: " + str(resp['marketCap']))
        else:
            print("The given stock symbol could not be found!")

    def usage(self, jarvis):
        jarvis.say("stock <stock_id>\t : Get details of stock identified by <stock_id>(one id at a time)", Fore.GREEN)
        jarvis.say("stock getid\t\t : Search stock id", Fore.GREEN)
        jarvis.say("stock help\t\t : Prints help", Fore.GREEN)
        jarvis.say("*** AVAILABLE ONLY FOR US EQUITIES ***", Fore.GREEN)

    def get_stock_id(self, jarvis, name):
        resp = requests.get('https://api.iextrading.com/1.0/ref-data/symbols')
        if resp.status_code == 200:
            data = resp.json()
            found = False
            for stock in data:
                if re.search(name.lower(), stock['name'].lower()):
                    found = True
                    jarvis.say(stock['symbol'] + "\t:\t" + stock['name'], Fore.GREEN)
            if not found:
                jarvis.say("The given name could not be found", Fore.RED)
        else:
            jarvis.say("The given name could not be found!", Fore.RED)
