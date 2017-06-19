import unittest
from mock import patch
from packages import forecast
from CmdInterpreter import CmdInterpreter


class ForecastTest(unittest.TestCase):

    @patch.object(forecast, 'main')
    def test_forecast_called_from_do_check(self, forecast_mock):
        CmdInterpreter('', '').do_check('check forecast')
        forecast_mock.assert_called()
