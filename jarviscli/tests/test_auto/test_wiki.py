import unittest
import packages.wiki as wiki

class WikiTest(unittest.TestCase):

    def test_search(self):
        d = wiki.search("Barack")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 10)

        d = wiki.search("sldjflsfkdslfjsl")
        self.assertEqual(d, "No articles with that name, try another item.")

    def test_suggest(self):
        d = wiki.suggest("barak obama")
        self.assertEqual(d, "barack obama")

        d = wiki.suggest("Barak")
        self.assertEqual(d, "No article with that name, try another item.")

    def test_summary(self):
        d = wiki.summary("Obama")
        self.assertIsInstance(d, unicode)

        d = wiki.summary("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = wiki.summary("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)

    def test_page(self):
        d = wiki.page("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = wiki.page("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)

    def test_random(self):
        d = wiki.random(1)
        self.assertIsInstance(d, unicode)

        d = wiki.random(5)
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)

if __name__ == '__main__':
    unittest.main()
