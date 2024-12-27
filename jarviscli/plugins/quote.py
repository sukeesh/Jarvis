import requests
from bs4 import BeautifulSoup

import json
from plugin import plugin, require


@require(network=True)
@plugin('quote')
class Quote():
    """
    quote prints quote for the day for you or quotes based on a given keyword
    """

    def __call__(self, jarvis, s):
        prompt = 'Press 1 to get the quote of the day \n or 2 to get quotes based on a keyword: '
        user_input = self.get_input(prompt, jarvis)

        if user_input == 1:
            self.get_quote_of_the_day(jarvis)
        else:
            text = 'Enter the keyword based on which you want to see quotes: '
            keyword = jarvis.input(text)
            self.get_keyword_quotes(jarvis, keyword)

    def get_quote_of_the_day(self, jarvis):
        res = requests.get(
            'https://quotes.rest/qod')
        if res.status_code == 200:
            data = res.text
            parse_json = json.loads(data)
            quote = parse_json['contents']['quotes'][0]['quote']
            jarvis.say(quote)
        else:
            jarvis.say(
                'Sorry, something went wrong. '
                'Please try again later or report this issue if it sustains.'
            )

    def get_keyword_quotes(self, jarvis, keyword):
        """
        shows quotes based on a keyword given by the user
        """

        while True:
            res = requests.get(f'https://www.brainyquote.com/search_results?x=0&y=0&q={keyword}')
            soup = BeautifulSoup(res.text, 'html.parser')
            quote_divs = soup.find_all('div', {'class': 'bqQt'})

            quotes = []
            for quote_div in quote_divs:
                quote_text = quote_div.find('a', {'title': 'view quote'}).text
                quotes.append(quote_text)

            num_quotes = len(quotes)
            current_quote = 0

            if num_quotes == 0:
                response = jarvis.input(
                    f'Sorry, no quotes were found for {keyword}. '
                    'Type a new keyword to try again or "exit" to leave: ')
                if response.lower() == 'exit':
                    break
                keyword = response
                continue

            while num_quotes > 0:
                if current_quote >= num_quotes:
                    current_quote = 0

                quote = quotes[current_quote]
                jarvis.say(quote)
                response = jarvis.input('Type "again" for another quote or "exit" to leave: ')

                if response.lower() == 'again':
                    current_quote = (current_quote + 1) % num_quotes

                if response.lower() == 'exit':
                    break

            break

    def contains_word(self, s, keyword):
        return (' ' + keyword.lower()) in s or (keyword.capitalize()) in s

    def get_input(self, prompt, jarvis):
        """
        checks if the input the user gave is valid(either 1 or 2)
        """

        while True:
            try:
                response = int(jarvis.input(prompt))
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
