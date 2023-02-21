from plugin import plugin
from colorama import Fore
from utilities.timedeltaUtilities import Timedelta_utilities
import datetime


def basetimer(jarvis, event_name, target_datetime, color=Fore.YELLOW,
              check_year=True):
    """
    Tells the time until a target event.
    Args:
        jarvis: jarvis parser.
        event_name (string): the name of the target event.
        target_datetime (datetime.datetime): the datetime of the event.
        color (Fore): optional text color modifier.
        check_year (bool): if not targeting a particular year,
        reset the date if the event has already happened.
    """
    actual_datetime = datetime.datetime.today()
    if check_year:
        # check if the event has already happened this year
        if actual_datetime > target_datetime:
            target_datetime = target_datetime.replace(
                year=actual_datetime.year + 1)
    if not check_year and actual_datetime > target_datetime:
        jarvis.say(f"Event {event_name} has already occurred.")
    else:
        time_until_event = target_datetime - actual_datetime
        jarvis.say(
            f"It\'s {Timedelta_utilities.format_time_delta(time_until_event)}"
            f" until {event_name}", color)


@plugin("christmas timer")
def christmastimer(jarvis, s):
    """
    Tells remaining time until Christmas.
    """
    actual_datetime = datetime.datetime.today()
    christmas_time = datetime.datetime(
        actual_datetime.year, 12, 24, 23, 59, 59)
    basetimer(jarvis, 'Christmas', christmas_time, Fore.GREEN)


@plugin("endofyear")
def endofyeartimer(jarvis, s):
    """
    Tells remaining time until the end of the year.
    """
    actual_datetime = datetime.datetime.today()
    end_of_year = datetime.datetime(actual_datetime.year, 12, 31, 23, 59, 59)
    basetimer(jarvis, 'End of the Year', end_of_year)
