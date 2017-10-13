# -*- coding: utf-8 -*-
import unittest
from mock import patch, call
from packages import forecast
from CmdInterpreter import CmdInterpreter
from colorama import Fore
from packages import mapps
import requests
import json


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


class ForecastTest(unittest.TestCase):

    def setUp(self):
        self.CI_instance = CmdInterpreter('', '')
        self.current_location = mapps.get_location()
        self.units = units = {
            'url_units': 'metric',
            'str_units': 'ºC'
        }
        if self.current_location['country_name'] == 'United States':
            self.units = {
                'url_units': 'imperial',
                'str_units': 'ºF'
            }

    @patch.object(forecast, 'main')
    def test_forecast_called_from_do_check(self, forecast_mock):
        self.CI_instance.do_check('check forecast')
        forecast_mock.assert_called()

    @patch.object(forecast, 'print_say')
    def test_header_as_expected_when_no_location(self, print_say_mock):
        my_city_and_country = "{},{}".format(
            self.current_location['city'],
            self.current_location['country_code']
        )
        with patch.object(requests, 'get', return_value=MyResponse) as get_mock:
            forecast.main(self.CI_instance, 'check forecast')
            get_mock.assert_called_with(
                "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
                "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={2}".format(
                    my_city_and_country,
                    '7',
                    self.units['url_units']
                )
            )

    @patch.object(forecast, 'print_say')
    def test_header_as_expected_with_location(self, print_say_mock):
        with patch.object(requests, 'get', return_value=MyResponse) as get_mock:
            forecast.main(self.CI_instance, 'check forecast in New York')
            get_mock.assert_called_with(
                "http://api.openweathermap.org/data/2.5/forecast/daily?q={0}&cnt={1}"
                "&APPID=ab6ec687d641ced80cc0c935f9dd8ac9&units={2}".format(
                    'New York',
                    '7',
                    self.units['url_units']
                )
            )

    @patch.object(forecast, 'print_say')
    def test_forecast_formatted_as_expected(self, print_say_mock):
        with patch.object(requests, 'get', return_value=MyResponse) as get_mock:
            forecast.main(self.CI_instance, 'Some location')
            last_call = call(
                "\tMin temperature: {} {}\n".format(
                    '17.0', self.units['str_units']),
                self.CI_instance,
                Fore.BLUE
            )
            third_call = call(
                "\tWeather: {}".format('Clear'),
                self.CI_instance,
                Fore.BLUE
            )
            self.assertEqual(last_call, print_say_mock.mock_calls[-1])
            self.assertEqual(third_call, print_say_mock.mock_calls[2])
