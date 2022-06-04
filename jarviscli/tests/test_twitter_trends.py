import unittest
from unittest import mock
import requests
from tests import PluginTest
from plugins.twitter_trends import TwitterTrends


class TwitterTrendsTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(TwitterTrends)
        self.test.jarvis = self.jarvis_api

    def test_available_countries(self):
        response = requests.get(
            "http://api-twitter-trends.herokuapp.com/location")
        self.assertTrue(response.ok)

    def test_sample_countries(self):
        # Test Greece country
        response = requests.get(
            f"http://api-twitter-trends.herokuapp.com/trends?location=greece")
        self.assertTrue(response.ok)

    def test_is_out_of_range_true(self):
        self.assertTrue(self.test.is_out_of_range(700))
        self.assertTrue(self.test.is_out_of_range(-10))

    def test_is_out_of_range_false(self):
        self.assertFalse(self.test.is_out_of_range(10))
        self.assertFalse(self.test.is_out_of_range(50))

    def test_is_exit_input(self):
        self.assertTrue(self.test.is_exit_input('exit'))
        self.assertFalse(self.test.is_exit_input('random'))

    def test_get_country_exit(self):
        PluginTest.queue_input(self, 'exit')
        result = self.test.get_country()
        self.assertEqual(result, 'exit')

    def test_get_country_number(self):
        PluginTest.queue_input(self, '-10')
        PluginTest.queue_input(self, '10')
        self.assertEqual(self.test.get_country(), 10)


if __name__ == '__main__':
    unittest.main()
