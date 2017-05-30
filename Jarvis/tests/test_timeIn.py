import unittest
from packages import timeIn
import time
import sys
from StringIO import StringIO

class TimeInTest(unittest.TestCase):

    def setUp(self):
        sys.stdout = StringIO()

    def test_timeIn(self):
        """ test the timeIn.main function against time.ctime """

        timeIn.main(self, "time in New York City, NY")
        sys.stdout.seek(0)
        output = sys.stdout.read()
        result = output.split(' ')[12][0:8]

        time_here = time.ctime(time.time()).split(' ')[3]

        self.assertEqual(result, time_here)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
