import unittest
from plugins.news import News

from tests import PluginTest


class NewsTest(PluginTest):
    def test_news(self):
        n = self.load_plugin(News)
        n.update_api_key(self.jarvis_api, "7488ba8ff8dc43459d36f06e7141c9e5")
        self.assertIsNotNone(n.get_headlines(self.jarvis_api))


if __name__ == '__main__':
    unittest.main()
