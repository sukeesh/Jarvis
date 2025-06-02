import unittest
from tests import PluginTest
from plugins import leap_year


class LeapYearTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(leap_year.leap_year)

    def test_divisible_by_400_and_100(self):
        self.test.run("2000")
        self.assertEqual(self.history_say().last_text(), "2000 is a leap year.")

    def test_divisible_by_100_and_not_400(self):
        self.test.run("1900")
        self.assertEqual(self.history_say().last_text(), "1900 is not a leap year.")

    def test_divisible_by_4_and_not_100(self):
        self.test.run("2008")
        self.assertEqual(self.history_say().last_text(), "2008 is a leap year.")

    def test_not_divisible_by_4(self):
        self.test.run("2017")
        self.assertEqual(self.history_say().last_text(), "2017 is not a leap year.")

    def test_invalid_input(self):
        self.test.run("abc")
        self.assertEqual(
            self.history_say().last_text(),
            "Wrong input. Please make sure you just enter an integer e.g. '2012'.",
        )


if __name__ == "__main__":
    unittest.main()
