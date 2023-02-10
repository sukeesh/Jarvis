from plugin import plugin
from colorama import Fore
from utilities.timedeltaUtilities import Timedelta_utilities
import datetime

@plugin("christmas timer")
def christmastimer(jarvis, s):
    """
    Tells the time till christmas
    """

    actual_datetime = datetime.datetime.today()
    christmas_time = datetime.datetime(actual_datetime.year, 12, 24, 23, 59, 59)

    time_till_christmas = christmas_time - actual_datetime

    jarvis.say(f"It\'s {Timedelta_utilities.format_time_delta(time_till_christmas)}" +
        " until christmas", Fore.YELLOW)
