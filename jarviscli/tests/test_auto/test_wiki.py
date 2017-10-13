import unittest
import packages.wiki as wiki


class WikiTest(unittest.TestCase):

    def test_search(self):
        d = wiki.search("Barack")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 10)

        d = wiki.search("sldjflsfkdslfjsl")
        self.assertEqual(d, "No articles with that name, try another item.")

    def test_summary(self):
        d = wiki.summary("Obama")
        self.assertIsInstance(d, unicode)

        d = wiki.summary("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = wiki.summary("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)

    def test_content(self):
        d = wiki.content("Obama")
        self.assertIsInstance(d, unicode)

        d = wiki.content("adfsklfdlksf")
        self.assertEqual(d, "No page matches, try another item.")

        d = wiki.content("mercury")
        self.assertIsInstance(d, list)
        self.assertEqual(len(d), 5)


if __name__ == '__main__':
    unittest.main()
