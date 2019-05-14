import unittest
from Jarvis import Jarvis
from plugins.quote import Quote

from tests import PluginTest


class QuoteTest(PluginTest):

    quotes = [
        {
            u'quote': (
                u'Traveling, you realize that differences are lost:'
                ' each city takes to resembling all cities, places exchange'
                ' their form, order, distances, a shapeless dust cloud invades'
                ' the continents.'),
            u'cat': u'travel',
            u'author': 'Italo Calvino'}]

    def setUp(self):
        self.test = self.load_plugin(Quote)

    def test_try_again(self):
        self.queue_input('exit')
        self.test.try_again('travel', self.jarvis_api)

    def test_contains_word(self):
        text = 'Friends show their love in times of trouble, not in happiness.'
        self.assertEqual(self.test.contains_word(text, 'friends'), True)
        self.assertEqual(self.test.contains_word(text, 'travel'), False)

    def test_get_input(self):
        self.queue_input('2')
        response = self.test.get_input('Enter yeahh: ', self.jarvis_api)
        self.assertEqual(response, 2)


if __name__ == '__main__':
    unittest.main()
