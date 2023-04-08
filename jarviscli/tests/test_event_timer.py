import unittest
from tests import PluginTest
from plugins.event_timer import christmastimer, endofyeartimer, basetimer
import datetime


class EventTimerTest(PluginTest):
    """
    Tests For Event Timer Plugin
    """

    def setUp(self):
        self.xmas_test = self.load_plugin(christmastimer)
        self.eoy_test = self.load_plugin(endofyeartimer)

    def test_xmas(self):
        self.xmas_test.run()
        self.assertIn("Christmas", self.history_say().last_text())

    def test_eoy(self):
        self.eoy_test.run()
        self.assertIn("End of the Year", self.history_say().last_text())

    def test_date_passed(self):
        old_datetime = datetime.datetime(1995, 1, 1)
        basetimer(self.jarvis_api, "Test Event", old_datetime,
                  check_year=False)
        self.assertEquals("Event Test Event has already occurred.",
                          self.history_say().last_text())

    def test_date_passed_with_year(self):
        old_datetime = datetime.datetime(1995, 1, 1)
        basetimer(self.jarvis_api, "Test Event", old_datetime,
                  check_year=True)
        self.assertIn("until", self.history_say().last_text())


if __name__ == '__main__':
    unittest.main()
