# -*- coding: utf-8 -*-
import unittest
from mock import patch, call
from plugins.converted import check_forecast
from packages import mapps
from colorama import Fore
import requests
import json


from tests import PluginTest


class MyResponse(requests.models.Response):
    text = json.dumps({
        "city": {
            "country": "GB",
            "name": "London"
        },
        "list": [
            {
                "temp": {
                    "min": 11.00,
                    "max": 21.00
                },
                "weather": [
                    {
                        "main": "Clear"
                    }
                ]
            },
            {
                "temp": {
                    "min": 17.00,
                    "max": 27.00
                },
                "weather": [
                    {
                        "main": "Rain"
                    }
                ]
            }
        ],
        "cnt": 2
    })
    status_code = 200


class ForecastTest(PluginTest):
    def setUp(self):
        self.current_location = mapps.get_location()
        self.units = {
            'url_units': 'metric',
            'str_units': 'ºC'
        }
        if self.current_location['country_name'] == 'United States':
            self.units = {
                'url_units': 'imperial',
                'str_units': 'ºF'
            }
        self.test = self.load_plugin(check_forecast)

    def test_header_as_expected_when_no_location(self):
        my_city_and_country = "{},{}".format(
            self.current_location['city'],
            self.current_location['country_code']
        )
        with patch.object(requests, 'get', return_value=MyResponse) as get_mock:
            self.test.run('')
            get_mock.assert_called_with(
                "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
                "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={2}".format(
                    my_city_and_country, '7', self.units['url_units']))

    def test_header_as_expected_with_location(self):
        with patch.object(requests, 'get', return_value=MyResponse) as get_mock:
            self.test.run('in New York')
            get_mock.assert_called_with(
                "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
                "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={2}".format(
                    'New York', '7', self.units['url_units']))

    def test_forecast_formatted_as_expected(self):
        with patch.object(requests, 'get', return_value=MyResponse) as _:
            self.test.run('Some location')
            last_call = "\tMin temperature: {} {}".format(
                '17.0', self.units['str_units'])
            third_call = "\tWeather: {}".format('Clear')

            self.assertEqual(last_call, self.history_say().last_text())
            self.assertEqual(third_call, self.history_say().view_text(3))


if __name__ == '__main__':
    unittest.main()
