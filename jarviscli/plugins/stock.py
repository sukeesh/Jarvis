import requests
from plugin import plugin


@plugin('stock')
class Stock:

    def __call__(self, jarvis, s):
        quote = input("Stock Symbol: ").replace(" ", "")
        self.get_stock_data(quote)

    @staticmethod
    def get_stock_data(quote):

        resp = requests.get(
            'https://api.iextrading.com/1.0/stock/' +
            quote +
            '/quote')

        if resp.status_code == 200:
            resp = resp.json()
            print("Price: " + str(resp['iexRealtimePrice']))
            print("Open: " + str(resp['open']))
            print("Close: " + str(resp['close']))
            print("Change: " + str(resp['changePercent']) + "%")
            print("MarketCap: " + str(resp['marketCap']))
        else:
            print("The given stock symbol could not be found!")
