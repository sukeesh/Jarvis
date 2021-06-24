import unittest
from tests import PluginTest
from plugins import wifi_password_getter
from colorama import Fore


class TestWifiPasswordGetter(PluginTest):
    """
    A test class that contains test cases for the methods of
    the wifi_password_getter plugin for Windows.
    """

    def setUp(self):
        self.test = self.load_plugin(
            wifi_password_getter.WifiPasswordGetterWINDOWS)

    def test_show_options_last_text(self):
        self.queue_input("2")
        profiles = ["profile_1", "profile_2", "profile_3"]
        self.test.show_options(self.jarvis_api, profiles)
        self.assertEqual(self.history_say().last_text(), "4: Exit")

    def test_get_choice_valid(self):
        self.queue_input("2")
        input_text = "Please select a number or Exit: "
        max_valid_value = 3
        self.assertEqual(
            self.test.get_choice(
                self.jarvis_api,
                input_text,
                max_valid_value),
            2)

    def test_get_choice_terminator(self):
        self.queue_input("3")
        input_text = "Please select a number or Exit: "
        max_valid_value = 3
        self.assertEqual(
            self.test.get_choice(
                self.jarvis_api, input_text, max_valid_value), -1)

    def test_get_choice_invalid(self):
        self.queue_input("7")
        self.queue_input("2")
        input_text = "Please select a number or Exit: "
        max_valid_value = 3
        self.test.get_choice(self.jarvis_api, input_text, max_valid_value)
        self.assertEqual(
            self.history_say().last_text(),
            "Invalid input! Enter a number from the choices provided.")
        self.assertEqual(self.history_say().last_color(), Fore.YELLOW)

    def test_get_choice_exception(self):
        self.queue_input("wrong_input")
        self.queue_input("2")
        input_text = "Please select a number or Exit: "
        max_valid_value = 3
        self.test.get_choice(self.jarvis_api, input_text, max_valid_value)
        self.assertEqual(
            self.history_say().last_text(),
            "Invalid input! Enter a number from the choices provided.")
        self.assertEqual(self.history_say().last_color(), Fore.YELLOW)


if __name__ == '__main__':
    unittest.main()
