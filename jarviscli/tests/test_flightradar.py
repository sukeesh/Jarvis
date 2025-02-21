import unittest
from tests import PluginTest
from plugins.flightradar import flightradar


class FlightradarTest(PluginTest):
    """
        this class is testing the flight radar plugin
    """
    
    def setUp(self):
        self.test = self.load_plugin(flightradar)

    def test_invalid_option_empty(self):
        """Test for correct output message if use letters instead of numbers 
        for first question"""
        self.queue_input("")
        expected_out= "Enter a vaild option"

        self.test.run("")
        self.assertEqual(self.history_say().last_text(), expected_out)
    def test_invalid_option_letters(self):
        """Test for correct output message if use letters instead of numbers 
        for first question"""
        self.queue_input("abba")
        expected_out= "Enter a vaild option"

        self.test.run("")
        self.assertEqual(self.history_say().last_text(), expected_out)
    def test_invalid_option_number(self):
        """Test for correct output message if use letters instead of numbers 
        for first question"""
        self.queue_input("15")
        expected_out= "Enter a vaild option"

        self.test.run("")
        self.assertEqual(self.history_say().last_text(), expected_out)

    def test_invalid_option_1_letters(self):
        """Test for correct output msg when after going 
        in to check airline flights an put letters instead of a number"""
        self.queue_input("1")
        self.queue_input("abba")
        self.test.run("")
        expected_out= "Enter a vaild option"    
        self.assertEqual(self.history_say().last_text(), expected_out)
    def test_invalid_option_1_number(self):
        """Test for correct output msg when after going 
        in to check airline flights and put a number outside the range"""
        self.queue_input("1")
        self.queue_input("15")
        self.test.run("")
        expected_out= "Enter a vaild option"    
        self.assertEqual(self.history_say().last_text(), expected_out)

    def test_empty_ICAO(self):
        """Test for correct output msg when inputing an empty ICAO field"""
        self.queue_input("1")
        self.queue_input("1")
        self.queue_input("")
        self.test.run("")
        expected_out= "Enter a ICAO"    
        self.assertEqual(self.history_say().last_text(), expected_out)
    def test_valid_ICAO(self):
        """Test for correct output msg when inputing an empty ICAO field"""
        self.queue_input("1")
        self.queue_input("1")
        self.queue_input("EZY")
        self.test.run("")
        self.assertTrue(self.history_say().contains('text',"EZY"))
    
    def test_invalid_option_2_letters(self):
        """Test for correct output msg when after going 
        in to check airline flights an put letters instead of a number"""
        self.queue_input("2")
        self.queue_input("abba")
        self.test.run("")
        expected_out= "Enter a vaild option"    
        self.assertEqual(self.history_say().last_text(), expected_out)
    def test_invalid_option_2_number(self):
        """Test for correct output msg when after going 
        in to check airline flights and put a number outside the range"""
        self.queue_input("2")
        self.queue_input("15")
        self.test.run("")
        expected_out= "Enter a vaild option"    
        self.assertEqual(self.history_say().last_text(), expected_out)
    

if __name__ == '__main__':
    unittest.main()
