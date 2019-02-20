import unittest
try:  # for python2
    from StringIO import StringIO
except ImportError:  # for python3
    from io import StringIO

from Jarvis import Jarvis
from plugins.evaluator import calculate

from tests import PluginTest


class EvaluatorTest(PluginTest):

    def setUp(self):
        self.test = self.load_plugin(calculate)

    def test_calc(self):
        # Test a basic calculation
        self.test.run("2 powER 7 PLUS (6.7 Minus 3) diVided BY 0.45 bY 3")
        output = self.history_say().last_text()
        result = 2 ** 7 + (6.7 - 3) / 0.45 / 3
        self.assertLess(abs(float(output) - result), 0.01)

        # And now for something a little more _complex_
        self.test.run("(1 pluS 9.1j)^3.14129 mINUS 2.712")
        output = self.history_say().last_text()
        result = (1 + 9.1j)**3.14129 - 2.712
        output = output.replace(' ', '').replace('*', '').replace('I', 'j')
        self.assertLess(abs(complex(output) - result), 0.01)


if __name__ == '__main__':
    unittest.main()
