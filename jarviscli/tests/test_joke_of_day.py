import unittest
from tests import PluginTest
from plugins.joke_of_day import joke_of_day
from mock import patch, call
import requests


class joke_of_day_test(PluginTest):
    """
    Tests For joke_of_day Plugin
    """

    def setUp(self):
        self.test = self.load_plugin(joke_of_day)

    def test_get_joke(self):
        with patch.object(requests, 'get') as get_mock:
            self.test.get_joke(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api.jokes.one/jod")


if __name__ == '__main__':
    unittest.main()
