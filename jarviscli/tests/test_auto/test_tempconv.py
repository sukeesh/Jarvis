# -*- coding: utf-8 -*-

import unittest
from plugins.tempconv import Tempconv

from tests import PluginTest


class TestTempconv(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(Tempconv)

    def test_tmp_valid_regex(self):
        """Test temperature converter's input-checking regex"""
        # test some true cases
        self.assertTrue(self.test.temp_valid_regex("32f"))
        self.assertTrue(self.test.temp_valid_regex("32F"))
        self.assertTrue(self.test.temp_valid_regex("-32f"))
        self.assertTrue(self.test.temp_valid_regex("-32F"))
        self.assertTrue(self.test.temp_valid_regex("100c"))
        self.assertTrue(self.test.temp_valid_regex("100C"))
        self.assertTrue(self.test.temp_valid_regex("-100c"))
        self.assertTrue(self.test.temp_valid_regex("-100C"))
        self.assertTrue(self.test.temp_valid_regex("32.32f"))
        self.assertTrue(self.test.temp_valid_regex("32.442F"))
        self.assertTrue(self.test.temp_valid_regex("14.1c"))
        self.assertTrue(self.test.temp_valid_regex("-33.8889C"))

        # test some false expressions
        self.assertFalse(self.test.temp_valid_regex(""))
        self.assertFalse(self.test.temp_valid_regex("C"))
        self.assertFalse(self.test.temp_valid_regex("F"))
        self.assertFalse(self.test.temp_valid_regex("32Ff"))
        self.assertFalse(self.test.temp_valid_regex("F32"))
        self.assertFalse(self.test.temp_valid_regex("-F"))

    def test_temp_conversion_c_to_f(self):
        """Test conversions from Celsius to Fahrenheit"""

        self.assertEqual(self.test.convert_c_to_f(0), 32.0)
        self.assertEqual(self.test.convert_c_to_f(100), 212.0)

    def test_temp_conversion_f_to_c(self):
        """Test conversions from Fahrenheit to Celsius"""

        self.assertEqual(self.test.convert_f_to_c(32), 0.0)
        self.assertEqual(self.test.convert_f_to_c(212), 100.0)


if __name__ == '__main__':
    unittest.main()
