from plugin import plugin
from colorama import Fore
from utilities.timedeltaUtilities import Timedelta_utilities
import datetime

@plugin("endofyear")
def endofyear(jarvis, s):
    """
    Tells the time till the end of the year
    """

    actual_datetime = datetime.datetime.today()
    end_of_year = datetime.datetime(actual_datetime.year, 12, 31, 23, 59, 59)

    time_till_end = end_of_year - actual_datetime

    jarvis.say(f"It\'s {Timedelta_utilities.format_time_delta(time_till_end)}" +
        " until the end of the year", Fore.YELLOW)