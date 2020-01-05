import unittest
from Jarvis import Jarvis
from tests import PluginTest  
from plugins.geocode import Geocoder


class GeocoderTest(PluginTest):
    """
    This class is testing the geocode plugin
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

    def test_2_valid_address(self):
        """
        Test that a valid address returns a match
        """
        input_addr = "1315 10th Street, Sacramento, CA 95814"
        cleaned_addr = "1315+10th+street+sacramento+ca+95814"
        self.test_geocoder(self.jarvis_api, input_addr)
        
        if self.test_geocoder.req:
            self.assertTrue(self.test_geocoder.output)


    def test_3_invalid_address(self):
        """
        Test that an invalid address returns no matches
        """
        input_addr = "this is not an address"
        self.test_geocoder(self.jarvis_api, input_addr)
        
        if self.test_geocoder.req:
            self.assertFalse(self.test_geocoder.output)

    def test_4_symbol_injection(self):
        """
        Test that all symbols are cleaned from the address input
        """
        input_addr = r"""~`!@#$%^&*()-={}[]:";'<>,./|\?"""
        self.test_geocoder(self.jarvis_api, input_addr)

        self.assertFalse(self.test_geocoder.cleaned_addr)


if __name__ == '__main__':
    unittest.main()
