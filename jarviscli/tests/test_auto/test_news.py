import unittest
from plugins.news import News

from tests import PluginTest


class NewsTest(PluginTest):
    def test_news(self):
        n = self.load_plugin(News)
        self.assertIsNotNone(n.get_news_json())


if __name__ == '__main__':
    unittest.main()
