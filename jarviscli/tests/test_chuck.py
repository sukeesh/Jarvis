import unittest
from tests import PluginTest
from plugins.chuck import chuck
from mock import patch, call
import requests


class ChuckTest(PluginTest):
    """
    Tests For Chuck Plugin
    """

    def setUp(self):
        self.test = self.load_plugin(chuck)

    def test_main(self):
        with patch.object(requests, 'get') as get_mock:
            self.test(self.jarvis_api, "")
            get_mock.assert_called_with(
                "https://api.chucknorris.io/jokes/random")


if __name__ == '__main__':
    unittest.main()
