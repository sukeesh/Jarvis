import unittest
from mock import patch
from packages import weather_pinpoint, weatherIn


class WeatherInTest(unittest.TestCase):
    def test_pinpoint_is_called_if_no_location_is_found(self):
        with patch.object(weather_pinpoint, 'main') as pinpoint_mock:
            weatherIn.main(self, 'weather in UnknownLocationhjbahbchjba')
            self.assertTrue(pinpoint_mock.called)

        with patch.object(weather_pinpoint, 'main') as pinpoint_mock:
            weatherIn.main(self, 'weather')
            self.assertTrue(pinpoint_mock.called)


if __name__ == '__main__':
    unittest.main()
