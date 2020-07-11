import unittest
from tests import PluginTest
from plugins.cat_fact import cat_fact
from mock import patch, call
import requests


class CatFactTest(PluginTest):
    """
    Tests For Cat Fact Plugin
    """

    def setUp(self):
        self.test = self.load_plugin(cat_fact)

    def test_main(self):
        with patch.object(requests, 'get') as get_mock:
            self.test(self.jarvis_api, "")
            get_mock.assert_called_with(
                "https://catfact.ninja/fact")


if __name__ == '__main__':
    unittest.main()
