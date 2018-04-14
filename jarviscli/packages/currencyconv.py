import requests
from bs4 import BeautifulSoup


def currencyconv(self, ammount, fr, to):

    res = requests.get('https://www.xe.com/currencyconverter/convert/?Amount=' +
                        ammount + '&From=' + fr + '&To=' + to )

    soup = BeautifulSoup(res.text, 'lxml')
    result = soup.find('span', {'class': 'uccResultAmount'})

    print result.get_text()
