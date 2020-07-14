import json
import unittest
from tests import PluginTest
from plugins.geocode import Geocoder


class MockResponse:
    """
    This class is used to create a mock Response from requests.get
    """

    def __init__(self, text):
        self.text = text

    def json(self):
        return json.loads(self.text)


class GeocoderTest(PluginTest):
    """
    This class is testing the geocode plugin.
    """

    def setUp(self):
        self.test_geocoder = self.load_plugin(Geocoder)

    def test_1_address_input(self):
        """
        Test that the input address is correctly stored and cleaned
        """
        input_addr = "1315 10th Street, Sacramento, CA 95814"
        cleaned_addr = "1315+10th+street+sacramento+ca+95814"
        self.test_geocoder(self.jarvis_api, input_addr)

        self.assertEqual(self.test_geocoder.input_addr, input_addr.lower())
        self.assertEqual(self.test_geocoder.cleaned_addr, cleaned_addr)

    def test_2_symbol_injection(self):
        """
        Test that all symbols are cleaned from the address input
        """
        input_addr = r"""~`!@#$%^&*()-={}[]:";'<>,./|\?"""
        self.test_geocoder(self.jarvis_api, input_addr)

        self.assertFalse(self.test_geocoder.cleaned_addr)

    def test_3_parse_valid_response(self):
        """
        Test that a mock Response is correctly parsed into output data
        """
        mock_data = ('{"result": {"addressMatches": [{"matchedAddress":'
                     '"100 Fake St", "coordinates": {"x": "0", "y": "100"}}]}}')
        mock_response = MockResponse(mock_data)
        mock_parsed = self.test_geocoder.parse_response(mock_response)
        expected_parsed = {'Address matched': '100 Fake St',
                           'Latitude': '100', 'Longitude': '0'}

        self.assertEqual(mock_parsed, expected_parsed)

    def test_4_parse_empty_response(self):
        """
        Test that parsing returns nothing from an empty mock Response
        """
        mock_data = '{"result": {"addressMatches": []}}'
        mock_response = MockResponse(mock_data)
        mock_parsed = self.test_geocoder.parse_response(mock_response)

        self.assertFalse(mock_parsed)


if __name__ == '__main__':
    unittest.main()
