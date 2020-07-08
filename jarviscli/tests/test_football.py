import unittest
from tests import PluginTest
from plugins.football import Football
from mock import patch, call
import requests
import datetime

"""
    Provided By Plugin Creator
"""
API_KEY = '1ebd3b92bf5041249f8c1e7a540ce98c'
headers = {'X-Auth-Token': API_KEY}


class FootballTest(PluginTest):
    """
    Tests For FootBall Plugin

    """

    def setUp(self):
        self.test = self.load_plugin(Football)

    def test_get_competition(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            self.queue_input("0")
            self.test.get_competition(self.jarvis_api)
            get_mock.assert_called_with(
                "https://api.football-data.org/v2/competitions?plan=TIER_ONE", headers=headers)

    def test_competition(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            compId = 1
            self.test.competition(self.jarvis_api, compId)
            get_mock.assert_called_with(
                "https://api.football-data.org/v2/competitions/{}/standings".format(compId), headers=headers)

    def test_matches(self):
        with patch.object(requests, 'get', headers=headers) as get_mock:
            compId = 1
            self.test.matches(self.jarvis_api, compId)
            get_mock.assert_called_with(
                "https://api.football-data.org/v2/matches?competitions={}".format(compId), headers=headers)


if __name__ == '__main__':
    unittest.main()
