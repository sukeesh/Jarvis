import unittest
from tests import PluginTest
from plugins.basketball import basketball
from mock import patch, call
import requests
import datetime
from packages.memory.memory import Memory


class BasketballTest(PluginTest):
    """
    Tests For Basketball Plugin
    !!! test will be executed only if user has added his own api.basketball.com API_KEY
    """

    def setUp(self):
        self.test = self.load_plugin(basketball)
        m = Memory("basketball.json")
        self.unable_to_test_plugin = False
        if m.get_data("API_KEY") is None:
            self.unable_to_test_plugin = True
        else:
            self.headers = {"x-rapidapi-host": "api-basketball.p.rapidapi.com", "x-rapidapi-key": m.get_data("API_KEY")}

    def test_todays_games(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.test.todays_games(self.jarvis_api)
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/games?date={}".format(date), headers=self.headers)

    def test_search_team(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.queue_input("boston")
            self.test.search_team(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/teams?search=boston", headers=self.headers)

    def test_search_league(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.queue_input("nba")
            self.test.search_league(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/leagues?search=nba", headers=self.headers)

    def test_list_leagues(self):
        if self.unable_to_test_plugin:
            return
        with patch.object(requests, 'get', headers=self.headers) as get_mock:
            self.test.get_api_key(self.jarvis_api)
            self.test.list_leagues(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/leagues", headers=self.headers)


if __name__ == '__main__':
    unittest.main()
