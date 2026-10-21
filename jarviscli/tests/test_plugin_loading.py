import unittest
from unittest import mock

from tests import PluginTest
from plugins.colorconverter import color_converter
from plugins.geolocation import geolocation


class ColorConverterTest(PluginTest):
    def setUp(self):
        self.converter = self.load_plugin(color_converter)

    @mock.patch('builtins.input', side_effect=['hex', 'rgb', '#ff0000'])
    def test_hex_to_rgb(self, _input):
        self.converter.run('')
        self.assertIn('RGB: (255, 0, 0)', self.history_say().last_text())

    @mock.patch('builtins.input', side_effect=['rgb', 'hex', '255,0,0'])
    def test_rgb_to_hex(self, _input):
        self.converter.run('')
        self.assertIn('HEX: #ff0000', self.history_say().last_text())


class GeolocationTest(PluginTest):
    def setUp(self):
        self.geolocation = self.load_plugin(geolocation)

    @mock.patch('plugins.geolocation.requests.get')
    def test_reports_location_from_api(self, mock_get):
        mock_get.return_value.json.return_value = {
            'city_name': 'Gainesville',
            'region_name': 'Florida',
            'country_name': 'United States',
            'latitude': 29.65,
            'longitude': -82.32,
            'as': 'Example ISP',
            'asn': '12345',
        }

        self.geolocation.run('8.8.8.8')

        mock_get.assert_called_once_with(
            'https://api.ip2location.io/',
            params={'ip': '8.8.8.8', 'format': 'json'},
        )
        self.assertIn(
            "It's located at Gainesville, Florida, United States.",
            self.history_say().view_text(),
        )
        self.assertIn(
            "Its coordinates are (29.65, -82.32).",
            self.history_say().view_text(),
        )


if __name__ == '__main__':
    unittest.main()
