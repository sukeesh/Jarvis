import unittest
from mock import patch
from packages import forecast
from CmdInterpreter import CmdInterpreter
from colorama import Fore


class ForecastTest(unittest.TestCase):

    def setUp(self):
        self.CI_instance = CmdInterpreter('', '')

    @patch.object(forecast, 'main')
    def test_forecast_called_from_do_check(self, forecast_mock):
        self.CI_instance.do_check('check forecast')
        forecast_mock.assert_called()

    @patch.object(forecast, 'print_say')
    def test_print_as_expected_when_no_location(self, print_say_mock):
        forecast.main(self.CI_instance, 'check forecast')
        print_say_mock.assert_called_with(
            "Weather forecast in the current location for the next 7 days.",
            self.CI_instance,
            Fore.BLUE
        )

    @patch.object(forecast, 'print_say')
    def test_print_as_expected_with_location(self, print_say_mock):
        forecast.main(self.CI_instance, 'check forecast in New York')
        print_say_mock.assert_called_with(
            "Weather forecast in New York for the next 7 days.",
            self.CI_instance,
            Fore.BLUE
        )
