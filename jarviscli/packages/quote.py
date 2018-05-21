import requests
from bs4 import BeautifulSoup

from six.moves import input
import json


def show_quote(self):

    user_input = get_input('Press 1 to get the quote of the day \n' +
                           'or 2 to get quotes based on a keyword: ')

    if user_input == 1:
        get_quote_of_the_day(self)
    else:
        keyword = input('Enter the keyword based on which ' +
                        'you want to see quotes: ')
        get_keyword_quotes(self, keyword)


def get_quote_of_the_day(self):
    res = requests.get('https://www.brainyquote.com/quotes_of_the_day.html')
    soup = BeautifulSoup(res.text, 'lxml')

    quote = soup.find('img', {'class': 'p-qotd'})
    print(quote['alt'])


def get_keyword_quotes(self, keyword):
    """
    shows quotes based on a keyword given by the user
    """

    res = requests.get('https://talaikis.com/api/quotes')
    quotes = json.loads(res.text)

    flag = False
    line = 1
    for quote in quotes:
        contains_word(quote['quote'], keyword)
        if contains_word(quote['quote'], keyword):
            print str(line) + '. ' + quote['quote']
            line = line + 1
            flag = True  # there is at least one quote

    if not flag:
        print('No quotes inlcude this word. PLease try one more time.\n')
        try_again(self, keyword)
    else:
        print('')
        try_again(self, keyword)


def try_again(self, keyword):
    again = input('Enter -again- to get more quotes or -exit- to leave: ')
    if again.lower() == "again":
        get_keyword_quotes(self, keyword)


def contains_word(sentence, keyword):
    return (' ' + keyword.lower() + ' ') in sentence


def get_input(prompt):
    """
    checks if the input the user gave is valid(either 0 or 1)
    """

    while True:
        try:
            response = int(input(prompt))
            print('')
        except ValueError:
            print("\nSorry, I didn't understand that.")
            continue

        if (response != 1) and (response != 2):
            print("\nSorry, your response is not valid.")
            continue
        else:
            break
    return response
