import unittest
from tests import PluginTest
from plugins.tennis import tennis
from mock import patch, call
import requests
from packages.memory.memory import Memory


class TennisTest(PluginTest):
    """
    Tests For Tennis Rankings Plugin
    !!! test will be executed only if user has added his own API_KEY
    """

    def setUp(self):
        self.test = self.load_plugin(tennis)
        m = Memory("tennis.json")
        self.unable_to_test_plugin = False
        if m.get_data("API_KEY") is None:
            self.unable_to_test_plugin = True
        else:
            self.headers = {"accept": "application/json"}

    def test_get_atp_top10(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.test.process_option(self.jarvis_api, 'atp')
            get_mock.assert_called_with(
                "https://api.sportradar.com/tennis/trial/v3/en/rankings?"
                "api_key=" + self.test.get_api_key(self.jarvis_api),
                headers=self.headers)

    def test_get_wta_top10(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.test.process_option(self.jarvis_api, 'wta')
            get_mock.assert_called_with(
                "https://api.sportradar.com/tennis/trial/v3/en/rankings?"
                "api_key=" + self.test.get_api_key(self.jarvis_api),
                headers=self.headers)


if __name__ == '__main__':
    unittest.main()
