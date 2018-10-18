import unittest
from packages import timeIn
import time
import datetime
import sys
try:  # python2
    from StringIO import StringIO
except ImportError:  # python3
    from io import StringIO


class TimeInTest(unittest.TestCase):
    def setUp(self):
        sys.stdout = StringIO()

    def test_timeIn(self):
        """ test the timeIn.main function against time.ctime """

        # call timeIn.main and redirect stdout to a StringIO object
        timeIn.main(self, "time in Greenwich, UK")
        sys.stdout.seek(0)
        output = sys.stdout.read()

        # What is ctime in your current locale?
        time_here = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
        # Create a datetime object for the api call
        output_list = output.split(' ')
        result = datetime.datetime.strptime(' '.join([output_list[-2],
                                                      output_list[-1][0:8]]),
                                            '%Y-%m-%d %H:%M:%S')

        # Create a timedelta object to adjust for your locale's timezone
        # print self.dst
        delta_tz = datetime.timedelta(
            hours=((time.timezone) / 3600.0 + int(self.dst)))
        result -= (delta_tz)
        # Create another timedelta object to give the API call a margin
        # of error since the HTTP request may have latency
        delta_delay = datetime.timedelta(seconds=10)
        self.assertAlmostEqual(result, time_here, delta=delta_delay)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
