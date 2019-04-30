import datetime


class WeekDay(object):

    day_tags = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]

    def __init__(self):
        self.today = datetime.datetime.now()

    def get_week_from_today(self):
        day_ind = self.today.isoweekday()
        reordered_week = self.day_tags[day_ind
                                       - 1:] + self.day_tags[:day_ind - 1]
        return reordered_week
