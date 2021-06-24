import unittest
from tests import PluginTest
from colorama import Fore
from plugins.international_day import InternationalDay
import os


class InternationalDayTest(PluginTest):
    """
    This class is testing the international day plugin
    """
    def setUp(self):
        self.test = self.load_plugin(InternationalDay)

    def test_validate_input_date_case1(self):
        input = self.test.validate_input_date("2021-09-21")
        self.assertTrue(input)

    def test_validate_input_date_case2(self):
        input = self.test.validate_input_date("2021-21-01")
        self.assertFalse(input)

    def test_find_international_day_case1(self):
        current_date = "2021-06-24"
        current_day = 24
        current_month = 6
        # The below file path runs only for Windows
        if (os.name in ("nt", "dos", "ce")):
            filepath = r'data\international_days.csv'
            with open(filepath) as csv_file:
                result = self.test.find_international_day(current_date,
                                                          current_day,
                                                          current_month, csv_file)
                expected_message = "The concerned date is " + Fore.YELLOW + \
                                   str(current_date) + Fore.RESET + \
                                   ", but there isn't an International" \
                                   " Day for today :("
                self.assertEqual(result, expected_message)

    def test_find_international_day_case2(self):
        current_date = "2021-02-11"
        current_day = 11
        current_month = 2
        # The below file path runs only for Windows
        if (os.name in ("nt", "dos", "ce")):
            filepath = r'data\international_days.csv'
            with open(filepath) as csv_file:
                result = self.test.find_international_day(current_date,
                                                          current_day,
                                                          current_month, csv_file)
                expected_message = "The concerned date is " + Fore.RESET +\
                                   Fore.YELLOW + \
                    str(current_date) + \
                    Fore.RESET + ", International Day" \
                    " of Women and Girls in Science"
                self.assertEqual(result, expected_message)

    def test_find_date(self):
        expected = '2021-06-24'
        current_date = self.test.find_date()
        self.assertEqual(str(current_date), expected)

    def test_split_date(self):
        date_to_split = self.test.find_date()
        expected_day = 24
        expected_month = 6
        date = self.test.split_date(date_to_split)
        self.assertEqual(date[0], expected_day)
        self.assertEqual(date[1], expected_month)


if __name__ == '__main__':
    unittest.main()
