from threading import Timer


def schedule(time_seconds, function, *args):
    """Call function(*args) in time_seconds seconds"""
    timer = Timer(time_seconds, function, args)
    timer.start()
    return timer


class Scheduler:
    def __init__(self):
        self._counter = -1
        self._events = {}

    def create_event(self, time_seconds, function, jarvis, *args):
        self._counter += 1

        timer = schedule(time_seconds, function, jarvis, self._counter, *args)
        self._events.update({self._counter: timer})
        return self._counter

    def cancel(self, schedule_id):
        if schedule_id not in self._events:
            print("Error! No event {}".format(schedule_id))
            return

        self._events[schedule_id].cancel()
        del self._events[schedule_id]

    def stop_all(self):
        for timer in self._events.values():
            timer.cancel()
