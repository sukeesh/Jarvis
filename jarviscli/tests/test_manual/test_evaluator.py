import unittest
import sys
try:  # for python2
    from StringIO import StringIO
except ImportError:  # for python3
    from io import StringIO
from colorama import Fore

from Jarvis import Jarvis
from plugins.evaluator import calculate


class EvaluatorTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()
        sys.stdout = StringIO()

    def test_calc(self):
        # Test a basic calculation
        calculate().run(self.jarvis._api, "2 powER 7 PLUS (6.7 Minus 3) diVided BY 0.45 bY 3")
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()
        result = 2 ** 7 + (6.7 - 3) / 0.45 / 3
        output = output.replace('\x1b[34m', '').replace('\x1b[39m', '')
        self.assertTrue(abs(float(output) - result) < 0.01)

        # And now for something a little more _complex_
        sys.stdout = StringIO()
        calculate().run(self.jarvis._api, "(1 pluS 9.1j)^3.14129 mINUS 2.712")
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()
        result = (1 + 9.1j)**3.14129 - 2.712
        output = output.replace('\x1b[34m', '').replace('\x1b[39m', '')
        output = output.replace(' ', '').replace('*', '').replace('I', 'j')
        self.assertTrue(abs(complex(output) - result) < 0.01)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
