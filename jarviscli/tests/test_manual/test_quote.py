import unittest
from Jarvis import Jarvis
from mock import patch
from plugins.quote import Quote

from tests import PluginTest


class QuoteTest(PluginTest):

    quotes = [{u'quote': (u'Traveling, you realize that differences are lost:'
                          ' each city takes to resembling all cities, places exchange'
                          ' their form, order, distances, a shapeless dust cloud invades'
                          ' the continents.'),
               u'cat': u'travel', u'author': 'Italo Calvino'}]

    def setUp(self):
        self.test = self.load_plugin(Quote)

    @patch('plugins.quote.input')
    def test_try_again(self, get_mock):
        get_mock.return_value = 'exit'
        self.test.try_again('travel', self.jarvis_api)

    def test_contains_word(self):
        text = 'Friends show their love in times of trouble, not in happiness.'
        self.assertEqual(self.test.contains_word(text, 'friends'), True)
        self.assertEqual(self.test.contains_word(text, 'travel'), False)

    @patch('plugins.quote.input')
    def test_get_input(self, get_mock):
        get_mock.return_value = '2'
        response = self.test.get_input('Enter yeahh: ', self.jarvis_api)
        self.assertEqual(response, 2)


if __name__ == '__main__':
    unittest.main()
