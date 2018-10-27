import unittest
from plugins.news import News


class NewsTest(unittest.TestCase):
    def test_news(self):
        n = News()
        self.assertIsNotNone(n.get_news_json())


if __name__ == '__main__':
    unittest.main()
