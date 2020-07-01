import unittest
from tests import PluginTest
from plugins.basketball import basketball
from mock import patch, call
import requests
import datetime


API_KEY = "b13ad5f4c1msh55b5d06158c224cp14d63djsnac01e7128355"
headers = {"x-rapidapi-host": "api-basketball.p.rapidapi.com", "x-rapidapi-key": API_KEY}


class BasketballTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(basketball)

    def test_todays_games(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            self.test.todays_games(self.jarvis_api)
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/games?date={}".format(date), headers=headers)

    def test_search_team(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            self.queue_input("boston")
            self.test.search_team(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/teams?search=boston", headers=headers)

    def test_search_league(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            self.queue_input("nba")
            self.test.search_league(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/leagues?search=nba", headers=headers)

    def test_list_leagues(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            self.test.list_leagues(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api-basketball.p.rapidapi.com/leagues", headers=headers)


if __name__ == '__main__':
    unittest.main()
