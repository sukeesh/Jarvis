import unittest

from tests import PluginTest


class JarvisAPITest(PluginTest):
    def test_get_float_int(self):
        self.queue_input('1')
        self.assertEqual(self.jarvis_api.input_number(""), 1)

    def test_get_float_comma(self):
        self.queue_input('12,6')
        self.assertEqual(self.jarvis_api.input_number('Enter a number: '), 12.6)

    def test_get_int(self):
        self.queue_input('42.1')
        self.queue_input('1')
        self.assertEqual(self.jarvis_api.input_number("", rtype=int), 1)

    def test_get_range(self):
        self.queue_input('-99')
        self.queue_input('100')
        self.queue_input('1')
        self.assertEqual(self.jarvis_api.input_number("", rmin=0, rmax=99), 1)


if __name__ == '__main__':
    unittest.main()
