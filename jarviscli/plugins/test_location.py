import unittest
from tests import PluginTest  
from plugins import location
import requests
from mock import patch, call


class LocationTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(location.location)

    def test_location_1(self):
        # run code
        self.test.run("")
         
        # verify that code works
        self.assertEqual(self.history_say().last_text(), " is your pin code")

    def test_location_get(self):
        with patch.object(requests, 'get') as get_mock:
            self.test(self.jarvis_api,'48.18199920654297 is your latitude')
            get_mock.assert_called_with(
                "http://api.ipstack.com/check?access_key=aafa3f03dc42cd4913a79fd2d9ce514d")
    

if __name__ == '__main__':
    unittest.main()