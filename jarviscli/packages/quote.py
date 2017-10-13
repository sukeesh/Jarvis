import requests
from bs4 import BeautifulSoup


def show_quote(self):
    res = requests.get('https://www.brainyquote.com/quotes_of_the_day.html')
    soup = BeautifulSoup(res.text, 'lxml')

    quote = soup.find('img', {'class': 'p-qotd'})
    print(quote['alt'])
