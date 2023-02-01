from plugin import plugin
from colorama import Fore
import datetime

@plugin("endofyear")
def endofyear(jarvis, s):
    """
    Tells the time till the end of the year
    """

    actual_datetime = datetime.datetime.today()
    end_of_year = datetime.datetime(actual_datetime.year, 12, 31, 23, 59, 59)

    time_till_end = end_of_year - actual_datetime

    jarvis.say(f"It\'s {format_time_delta(time_till_end)}" +
        " until the end of the year", Fore.YELLOW)


def format_time_delta(t) -> str:
    remaining_secs = t.seconds % 3600
    time_dict = {
        'days' : t.days,
        'hours' : int(t.seconds / 3600),
        'minutes' : int(remaining_secs / 60),
        'seconds' : remaining_secs % 60
    }

    new_timedict = {}
    # create new dictionary with the keys being the right numeric value
    for element in time_dict:
        if time_dict[element] == 1:
            new_timedict[element[0:len(element)-1]] = time_dict[element]
        else:
            new_timedict[element] = time_dict[element]

    # store keys and values in a list
    # for easier access
    measures = list(new_timedict.keys())
    values = list(new_timedict.values())
    
    timedelta = ''
    for i in range(len(values)):
        timedelta += f'{values[i]} {measures[i]}, '

    # ignore the last 2 characters ', '
    return timedelta[:-2]