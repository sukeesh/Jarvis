import unittest
from Jarvis import Jarvis

import requests
from bs4 import BeautifulSoup
from six.moves import input
from mock import Mock, patch

from packages import quote
from packages.quote import get_keyword_quotes
from packages.quote import try_again
from packages.quote import contains_word
from packages.quote import get_input


class QuoteTest(unittest.TestCase):

    quotes = [{u'quote': u'Traveling, you realize that differences are lost:' +
               ' each city takes to resembling all cities, places exchange' +
               ' their form, order, distances, a shapeless dust cloud invades' +
               ' the continents.',
               u'cat': u'travel', u'author': 'Italo Calvino'}]

    def setUp(self):
        self = Jarvis()

    @patch('packages.quote.requests.get')
    @patch('packages.quote.json.loads', return_value=quotes)
    @patch('packages.quote.try_again')
    def test_get_keyword_quotes(self, get_mock, get_json, get_try_again):
        get_keyword_quotes(self, 'travel')

    @patch('packages.quote.input')
    def test_try_again(self, get_mock):
        get_mock.return_value = 'exit'
        try_again(self, 'travel')

    def test_contains_word(self):
        self.assertEqual(contains_word('Friends show their love in' +
                                       'times of trouble, not in happiness. ',
                                       'friends'), True)
        self.assertEqual(contains_word('Friends show their love in' +
                                       'times of trouble, not in happiness. ',
                                       'travel'), False)

    @patch('packages.quote.input')
    def test_get_input(self, get_mock):
        get_mock.return_value = '2'
        response = get_input('Enter yeahh: ')
        self.assertEqual(response, 2)


if __name__ == '__main__':
    unittest.main()
