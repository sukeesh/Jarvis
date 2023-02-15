import unittest
from tests import PluginTest  
from plugins.spinthewheel import spin


class SpinTheWheelTest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(spin)

    def test_Spin_1(self):
        # run code
        self.queue_input("8,8,88,8")
        self.test.run(self.jarvis_api)
        
        # verify that code works
        self.assertEqual(self.history_say().last_text(), '')


if __name__ == '__main__':
    unittest.main()
