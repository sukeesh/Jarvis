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
        result = output.split(' ')[10][0:8]

        # What is ctime in you current local?
        time_here = time.ctime(time.time()).split(' ')[3]

        # Adjust 'result' variable for your current local's timezone
        adjustment = time.timezone / 3600
        result_list = result.split(':')
        hour = (int(result_list[0]) - adjustment) % 24
        result = ':'.join([str(hour), result_list[1], result_list[2]])   
            
        self.assertEqual(result, time_here)

    def tearDown(self):
        sys.stdout = sys.__stdout__


if __name__ == '__main__':
    unittest.main()
