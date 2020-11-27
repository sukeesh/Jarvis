import unittest
from tests import PluginTest
from plugins import hex


class HexTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(hex.hex)

    def test_0(self):
        self.test.run("0")
        self.assertEqual(self.history_say().last_text(), "0")

    def test_2(self):
        self.test.run("2")
        self.assertEqual(self.history_say().last_text(), "2")

    def test_4932(self):
        self.test.run("4932")
        self.assertEqual(self.history_say().last_text(), "1344")

    def test_negative_1205(self):
        self.test.run("-1205")
        self.assertEqual(self.history_say().last_text(), "-4b5")


if __name__ == '__main__':
    unittest.main()
