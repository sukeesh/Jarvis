import unittest
from tests import PluginTest  
from plugins.pi import next_pi


class PITest(PluginTest):
    def setUp(self):
        self.test = self.load_plugin(next_pi)

    def test_PI_1(self):
        # run code
        self.queue_input("")
        self.test.run("n")
        
        # verify that code works
        self.assertEqual(self.history_say().last_text(), 'Pi equals 3.14...')


if __name__ == '__main__':
    unittest.main()
