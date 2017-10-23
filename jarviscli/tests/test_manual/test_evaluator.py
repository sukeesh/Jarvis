import unittest
import sys
try:  # for python2
    from StringIO import StringIO
except ImportError:  # for python3
    from io import StringIO
from colorama import Fore

from Jarvis import Jarvis
from packages.evaluator import calc


class EvaluatorTest(unittest.TestCase):

    def setUp(self):
        self.jarvis = Jarvis()
        sys.stdout = StringIO()

    def test_calc(self):
        # Test a basic calculation
        calc("2 powER 7 PLUS (6.7 Minus 3) diVided BY 0.45 bY 3", self.jarvis)
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()
        result = Fore.BLUE + str(2 ** 7 + (6.7 - 3) / 0.45 / 3) + Fore.RESET
        self.assertEqual(output, result)

        # And now for something a little more _complex_
        sys.stdout = StringIO()
        calc("(1 pluS 9.1j)^3.14129 mINUS 2.712", self.jarvis)
        sys.stdout.seek(0)
        output = sys.stdout.read().strip()
        result = Fore.BLUE + str((1 + 9.1j)**3.14129 - 2.712) + Fore.RESET
        self.assertEqual(output, result)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
