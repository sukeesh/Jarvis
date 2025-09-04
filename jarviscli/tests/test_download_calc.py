import unittest
from tests import PluginTest
from plugins import download_calc


class DownloadCalcTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(download_calc.download_calc)

    def test_correct1(self):
        self.queue_input("15.5gb")
        self.queue_input("2.5mb")
        self.test(self.jarvis_api, "")

        expected = "Download will complete in approximately 1 hours 45 minutes."
        self.assertEqual(self.history_say().last_text(), expected)

    def test_correct2(self):
        self.queue_input("23.3gb")
        self.queue_input("783kb")
        self.test(self.jarvis_api, "")

        expected = "Download will complete in approximately 8 hours 40 minutes."
        self.assertEqual(self.history_say().last_text(), expected)

    def test_correct3(self):
        self.queue_input("1.3tb")
        self.queue_input("0.4tb")
        self.test(self.jarvis_api, "")

        expected = "Download will complete in approximately 3 seconds."
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_datasize1(self):
        self.queue_input("15.5agb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "Invalid format, please try again, or cancel with c: "
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_datasize2(self):
        self.queue_input("15.5.5gb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "The provided download size is invalid."
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_datasize3(self):
        self.queue_input("gb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "Invalid format, please try again, or cancel with c: "
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_download_speed1(self):
        self.queue_input("15.5gb")
        self.queue_input("2.5amb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "Invalid format, please try again, or cancel with c: "
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_download_speed2(self):
        self.queue_input("15.5gb")
        self.queue_input("2.5.5mb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "The provided download speed is invalid."
        self.assertEqual(self.history_say().last_text(), expected)

    def test_incorrect_download_speed3(self):
        self.queue_input("15.5gb")
        self.queue_input("mb")
        self.queue_input("c")
        self.test(self.jarvis_api, "")

        expected = "Invalid format, please try again, or cancel with c: "
        self.assertEqual(self.history_say().last_text(), expected)


if __name__ == '__main__':
    unittest.main()
