import unittest
from Jarvis import Jarvis

import requests
from bs4 import BeautifulSoup
from six.moves import input
from mock import Mock, patch

from plugins.quote import Quote


test = Quote()


class QuoteTest(unittest.TestCase):

    quotes = [{u'quote': u'Traveling, you realize that differences are lost:' +
               ' each city takes to resembling all cities, places exchange' +
               ' their form, order, distances, a shapeless dust cloud invades' +
               ' the continents.',
               u'cat': u'travel', u'author': 'Italo Calvino'}]

    def setUp(self):
        self.jarvis = Jarvis()._api

    @patch('plugins.quote.requests.get')
    @patch('plugins.quote.json.loads', return_value=quotes)
    @patch('plugins.quote.Quote.try_again')
    def test_get_keyword_quotes(self, get_mock, get_json, get_try_again):
        Quote().get_keyword_quotes(self.jarvis, 'travel')

    @patch('plugins.quote.input')
    def test_try_again(self, get_mock):
        get_mock.return_value = 'exit'
        Quote().try_again(self.jarvis, 'travel')

    def test_contains_word(self):
        self.assertEqual(Quote().contains_word('Friends show their love in' +
                                               'times of trouble, not in happiness. ',
                                               'friends'), True)
        self.assertEqual(Quote().contains_word('Friends show their love in' +
                                               'times of trouble, not in happiness. ',
                                               'travel'), False)

    @patch('plugins.quote.input')
    def test_get_input(self, get_mock):
        get_mock.return_value = '2'
        response = Quote().get_input('Enter yeahh: ', self.jarvis)
        self.assertEqual(response, 2)


if __name__ == '__main__':
    unittest.main()
