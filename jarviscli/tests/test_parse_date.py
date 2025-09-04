import unittest
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from utilities.textParser import parse_date


class ParseDateTest(unittest.TestCase):
    def assert_datetime_equal(self, actual_output, expected_output, compare_time=True):
        """
        Helper method to compare datetime objects.
        
        Args:
            actual_output: Tuple of (skip, datetime) from parse_date
            expected_output: Tuple of (skip, datetime) for comparison
            compare_time: Boolean to determine if time should be compared
        """
        actual_skip, actual_dt = actual_output
        expected_skip, expected_dt = expected_output
        
        # Compare skip values
        self.assertEqual(actual_skip, expected_skip)
        
        if compare_time:
            # Compare up to seconds
            self.assertEqual(
                actual_dt.replace(microsecond=0),
                expected_dt.replace(microsecond=0)
            )
        else:
            # Compare only the date part
            self.assertEqual(
                actual_dt.replace(hour=0, minute=0, second=0, microsecond=0),
                expected_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            )

    def test_date_formats(self):
        """Test date format patterns."""
        test_cases = [
            ("2025-02-18", (1, datetime(2025, 2, 18))),
            ("25-02-19", (1, datetime(2025, 2, 19))),
            ("19.02.2025", (1, datetime(2025, 2, 19))),
            ("19.02.25", (1, datetime(2025, 2, 19))),
            ("2025-12-31", (1, datetime(2025, 12, 31))),
            ("2025-01-01", (1, datetime(2025, 1, 1))),
        ]
        for test_string, expected in test_cases:
            with self.subTest(test_string=test_string):
                self.assert_datetime_equal(parse_date(test_string), expected, False)

    def test_time_formats(self):
        """Test time format patterns."""
        today = datetime.today()
        test_cases = [
            ("14:30", (1, datetime.combine(today.date(), datetime.strptime("14:30", "%H:%M").time()))),
            ("2:30PM", (1, datetime.combine(today.date(), datetime.strptime("2:30PM", "%I:%M%p").time()))),
            ("00:00", (1, datetime.combine(today.date(), datetime.strptime("00:00", "%H:%M").time()))),
            ("11:59PM", (1, datetime.combine(today.date(), datetime.strptime("11:59PM", "%I:%M%p").time()))),
            ("9:00", (1, datetime.combine(today.date(), datetime.strptime("09:00", "%H:%M").time()))),
            ("9:00AM", (1, datetime.combine(today.date(), datetime.strptime("09:00AM", "%I:%M%p").time()))),
        ]
        for test_string, expected in test_cases:
            with self.subTest(test_string=test_string):
                self.assert_datetime_equal(parse_date(test_string), expected, True)

    def test_relative_time(self):
        """Test relative time expressions."""
        base_time = datetime.now()
        test_cases = [
            ("in 1 second", (3, base_time + timedelta(seconds=1))),
            ("in 1 minute", (3, base_time + timedelta(minutes=1))),
            ("in 1 hour", (3, base_time + timedelta(hours=1))),
            ("in 1 day", (3, base_time + timedelta(days=1))),
            ("in 1 week", (3, base_time + timedelta(weeks=1))),
            ("in 1 month", (3, base_time + relativedelta(months=1))),
            ("in 1 year", (3, base_time + relativedelta(years=1))),
            ("in 2 days and 3 hours", (6, base_time + timedelta(days=2, hours=3))),
        ]
        for test_string, expected in test_cases:
            with self.subTest(test_string=test_string):
                self.assert_datetime_equal(parse_date(test_string), expected, True)

    def test_next_weekday(self):
        """Test next weekday expressions."""
        weekdays = [
            ("Monday", 0),
            ("Tuesday", 1),
            ("Wednesday", 2),
            ("Thursday", 3),
            ("Friday",  4),
            ("Saturday", 5),
            ("Sunday", 6),
        ]
        for weekday, target_day in weekdays:
            test_string = f"next {weekday}"
            today = datetime.now()
            days_until = target_day - today.weekday()
            if days_until <= 0: 
                days_until += 7
                
            expected_time = today + timedelta(days=days_until)
            expected_output = (2, expected_time)
            
            with self.subTest(weekday=weekday):
                self.assert_datetime_equal(parse_date(test_string), expected_output, False)


if __name__ == '__main__':
    unittest.main()