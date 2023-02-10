import datetime

class Timedelta_utilities:

    def format_time_delta(t: datetime.timedelta) -> str:
        """
        Function takes timedelta and puts it into textual format
        """

        remaining_secs = t.seconds % 3600
        time_dict = {
            'days' : t.days,
            'hours' : int(t.seconds / 3600),
            'minutes' : int(remaining_secs / 60),
            'seconds' : remaining_secs % 60
        }

        new_timedict = {}
        # create new dictionary with the keys being the right numeric textual value
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