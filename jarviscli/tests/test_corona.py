import unittest
from tests import PluginTest
from plugins.corona import CoronaInfo
from mock import patch, call
import requests


class CoronaInfoTest(PluginTest):
    """
    Tests For CoronaInfo Plugin
    """

    def setUp(self):
        self.test = self.load_plugin(CoronaInfo)

    def test_get_corona_info(self):
        with patch.object(requests, 'get') as get_mock:
            self.test.get_corona_info("usa")
            get_mock.assert_called_with(
                "https://api.covid19api.com/summary")


if __name__ == '__main__':
    unittest.main()
