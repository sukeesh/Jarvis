import unittest
from tests import PluginTest
from plugins.scan_network import scan


class ScanNetworkTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(scan)

    def test_TESTCASE_1(self):
        if not self.test.valid:
            return

        # run code
        self.test.run('127.0.0.1')

        # verify that code works
        self.assertIn('127.0.0.1', self.history_say().view_text())


if __name__ == '__main__':
    unittest.main()
