import unittest
import plugins.wiki as wiki

from tests import PluginTest


class WikiTest(PluginTest):

    def setUp(self):
        self.wiki = self.load_plugin(wiki.Wiki)

    def test_search(self):
        d = self.wiki.search("Barack")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 10)

        d = self.wiki.search("sldjflsfkdslfjsl")
        self.assertEqual(d, "No articles with that name, try another item.")

    def test_summary(self):
        d = self.wiki.summary("Obama")
        try:  # python2
            self.assertIsInstance(d, unicode)
        except NameError:  # python3 unicode not defined in python3
            self.assertIsInstance(d, str)
        d = self.wiki.summary("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = self.wiki.summary("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)

    def test_content(self):
        d = self.wiki.content("Obama")
        try:  # python2
            self.assertIsInstance(d, unicode)
        except NameError:  # python3
            self.assertIsInstance(d, str)

        d = self.wiki.content("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = self.wiki.content("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)


if __name__ == '__main__':
    unittest.main()
