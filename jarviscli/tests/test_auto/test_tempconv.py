# -*- coding: utf-8 -*-

import unittest
from packages.tempconv import temp_valid_regex, convert_c_to_f, convert_f_to_c


class TestTempValidRegex(unittest.TestCase):
    def test_regex(self):
        """Test temperature converter's input-checking regex"""

        # test some true cases
        self.assertTrue(temp_valid_regex("32f"))
        self.assertTrue(temp_valid_regex("32F"))
        self.assertTrue(temp_valid_regex("-32f"))
        self.assertTrue(temp_valid_regex("-32F"))
        self.assertTrue(temp_valid_regex("100c"))
        self.assertTrue(temp_valid_regex("100C"))
        self.assertTrue(temp_valid_regex("-100c"))
        self.assertTrue(temp_valid_regex("-100C"))
        self.assertTrue(temp_valid_regex("32.32f"))
        self.assertTrue(temp_valid_regex("32.442F"))
        self.assertTrue(temp_valid_regex("14.1c"))
        self.assertTrue(temp_valid_regex("-33.8889C"))

        # test some false expressions
        self.assertFalse(temp_valid_regex(""))
        self.assertFalse(temp_valid_regex("C"))
        self.assertFalse(temp_valid_regex("F"))
        self.assertFalse(temp_valid_regex("32Ff"))
        self.assertFalse(temp_valid_regex("F32"))
        self.assertFalse(temp_valid_regex("-F"))


class TestTempConversions(unittest.TestCase):

    def test_c_to_f(self):
        """Test conversions from Celsius to Fahrenheit"""

        self.assertEqual(convert_c_to_f(0), 32.0)
        self.assertEqual(convert_c_to_f(100), 212.0)

    def test_f_to_c(self):
        """Test conversions from Fahrenheit to Celsius"""

        self.assertEqual(convert_f_to_c(32), 0.0)
        self.assertEqual(convert_f_to_c(212), 100.0)
