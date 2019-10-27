import requests
import warnings
from bs4 import BeautifulSoup
from plugin import plugin, require


@require(network=True)
@plugin('google')

class Scraper():

    """
    Runs a basic search and returns the default answer provided by google.
    Google's default answers all have a class contaning BNeawe, s3v9rd, orAP7Wnd,
    so we can just run a google query and parse the results

    example: google What is the Large Hadron Collider?
    """
    
    def __call__(self, jarvis, s):
        jarvis.say(self.search(s))


    def search(self, question):
        
        query = '+'.join(question.split(' '))
        url = 'https://www.google.com/search?q={}&ie=utf-8&oe=utf-8'.format(query)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        google_answers = soup.find_all("div", {"class": "BNeawe iBp4i AP7Wnd"})
        for answer in google_answers:
            if answer.text:
                return self.parse_result(answer.text)


        first_answers = soup.find_all("div", {"class": "BNeawe s3v9rd AP7Wnd"})
        for answer in first_answers:
            if answer.text:
                return self.parse_result(answer.text)

        
        all_div = soup.find_all("div")
        google_answer_keys = ['BNeawe', 's3v9rd', 'AP7Wnd', 'iBp4i']

        for div in all_div:
            for key in google_answer_keys:
                if key in div:
                    return self.parse_result(div.text)

        return 'No Answers Found'

        
    def parse_result(self, result):
        result = result.split('\n')[0]
        if result.endswith('Wikipedia'):
            result = result[:result.find('Wikipedia')]

        return result