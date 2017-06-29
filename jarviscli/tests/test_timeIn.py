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

        # call timeIn.main and redirect stdout to a StringIO object
        timeIn.main(self, "time in Greenwich, UK")
        sys.stdout.seek(0)
        output = sys.stdout.read()

        # What is ctime in you current local?
        time_here = time.ctime(time.time()).split(' ')

        # fix indices if the day of month is one or two digits long
        if '' in time_here:
            index = time_here.index('')
            time_here = time_here[0:index] + time_here[index+1:]
        time_here = time_here[3]

        # Adjust 'result' variable for your current local's timezone
        result = output.split(' ')[10][0:8]
        adjustment = time.timezone / 3600
        result_list = result.split(':')
        hour = (int(result_list[0]) - adjustment) % 24
        result = ':'.join([str(hour), result_list[1], result_list[2]])

        self.assertEqual(result, time_here)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
