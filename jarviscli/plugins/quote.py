import requests
import bs4

from six.moves import input
import json
from plugin import Plugin


class Quote(Plugin):
    """
    quote prints quote for the day for you or quotes based on a given keyword
    """
    def require(self):
        yield ("network", True)

    def complete(self):
        pass

    def alias(self):
        pass

    def run(self, jarvis, s):
        user_input = self.get_input('Press 1 to get the quote of the day \n' +
                                    'or 2 to get quotes based on a keyword: ', jarvis)

        if user_input == 1:
            self.get_quote_of_the_day(jarvis)
        else:
            keyword = input('Enter the keyword based on which ' +
                            'you want to see quotes: ')
            self.get_keyword_quotes(jarvis, keyword)

    def get_quote_of_the_day(self, jarvis):
        res = requests.get('https://www.brainyquote.com/quotes_of_the_day.html')
        soup = bs4.BeautifulSoup(res.text, 'lxml')

        quote = soup.find('img', {'class': 'p-qotd'})
        jarvis.say(quote['alt'])

    def get_keyword_quotes(self, jarvis, keyword):
        """
        shows quotes based on a keyword given by the user
        """

        res = requests.get('https://talaikis.com/api/quotes')
        quotes = json.loads(res.text)

        flag = False
        line = 1
        for quote in quotes:
            self.contains_word(quote['quote'], keyword)
            if self.contains_word(quote['quote'], keyword):
                jarvis.say(str(line) + '. ' + quote['quote'])
                line = line + 1
                flag = True  # there is at least one quote

        if not flag:
            jarvis.say('No quotes inlcude this word. PLease try one more time.\n')
            self.try_again(keyword, jarvis)
        else:
            jarvis.say('')
            self.try_again(keyword, jarvis)

    def try_again(self, keyword, jarvis):
        again = input('Enter -again- to get more quotes or -exit- to leave: ')
        if again.lower() == "again":
            self.get_keyword_quotes(jarvis, keyword)

    def contains_word(self, s, keyword):
        return (' ' + keyword.lower()) in s or (keyword.capitalize()) in s

    def get_input(self, prompt, jarvis):
        """
        checks if the input the user gave is valid(either 1 or 2)
        """

        while True:
            try:
                response = int(input(prompt))
                jarvis.say('')
            except ValueError:
                jarvis.say("\nSorry, I didn't understand that.")
                continue

            if (response != 1) and (response != 2):
                jarvis.say("\nSorry, your response is not valid.")
                continue
            else:
                break
        return response
