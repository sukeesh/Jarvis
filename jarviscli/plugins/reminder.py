import json
import time
import datetime

from pick import pick
from colorama import Fore
from six.moves import input
from pytimeparse.timeparse import timeparse

from plugin import plugin, Plugin
from utilities.textParser import parse_date


"""
Module content:
* RemindTodoBase: Shared functionality between Remind and Todo
* TododBase:  Based on RemindTodoBase; implements functionality required for
              RemindTodoBase to work
* RemindBase: Based on RemindTodoBase; implements functionality required for
              RemindTodoBase to work PLUS other functionality
* Plugins (Todo, Todo_Add, Todo_Remove, Remind, Remind_At, Remind_In,
          Remind_Remove) - oneliner based on TodoBase and RemindBase to
          "export" functionality as Plugins

"""

class RemindTodoBase:
    def get_data(self, jarvis):
        remind_todo_json = jarvis.get_data(self.get_key())
        if remind_todo_json is None:
            remind_todo_json = "[]"
            jarvis.add_data(self.get_key(), remind_todo_json)

        try:
            remind_todo_list = json.loads(remind_todo_json)
        except json.decoder.JSONDecodeError:
            jarvis.say(
                "Could not read Remind / Todo List. Sorry, \
                        that should not have happend...", Fore.RED)
            remind_todo_json = "[]"
            jarvis.update_data(self.get_key(), remind_todo_json)
            remind_todo_list = json.loads(remind_todo_json)

        return remind_todo_list

    def save_data(self, jarvis, remind_todo_list):
        jarvis.update_data(self.get_key(), json.dumps(remind_todo_list))

    def get_next_id(self, jarvis):
        next_id = jarvis.get_data(self.get_key_next_id())
        if next_id is None:
            next_id = 0
            jarvis.add_data(self.get_key_next_id(), next_id)

        jarvis.update_data(self.get_key_next_id(), next_id + 1)
        return next_id

    def remove(self, jarvis, s):
        data = self.get_data(jarvis)

        if s.startswith("everything"):
            for entry in data:
                self.clean_up_entry(jarvis, entry)

            data = []
            self.save_data(jarvis, data)

            jarvis.say("ok")
            return

        # open selection menu
        data = self.sort(data)
        ask_str = []
        for entry in data:
            ask_str.append(self.format(entry))

        title = 'Please choose task to remove (select with space)'
        selected = pick(ask_str, title, multi_select=True)
        selected = [entry[1] for entry in selected]

        new_data = []
        for index in range(len(data)):
            entry = data[index]
            if index not in selected:
                new_data.append(entry)
            else:
                self.clean_up_entry(jarvis, entry)

        self.save_data(jarvis, new_data)

    def print(self, jarvis):
        todo_list = self.get_data(jarvis)
        todo_list = self.sort(todo_list)

        if len(todo_list) == 0:
            jarvis.say("No entry!")
        for entry in todo_list:
            jarvis.say(self.format(entry))


class TodoBase(RemindTodoBase):
    def get_key(self):
        return "todo"

    def get_key_next_id(self):
        return "todo_next_id"

    def require(self):
        pass

    def alias(self):
        pass

    def complete(self):
        pass

    def add(self, jarvis, message, complete=0, priority=-1):
        data = self.get_data(jarvis)
        next_id = self.get_next_id(jarvis)
        new_entry = {
            'message': message,
            'complete': complete,
            'priority': priority,
            'id': next_id
        }
        data.append(new_entry)
        self.save_data(jarvis, data)

    def clean_up_entry(self, jarvis, entry):
        pass

    def format(self, entry):
        return entry['message']

    def sort(self, todo_list):
        return sorted(todo_list, key=lambda entry: entry['priority'])


class RemindBase(RemindTodoBase):
    def get_key(self):
        return "remind"

    def get_key_next_id(self):
        return "todo_next_id"

    def require(self):
        pass

    def alias(self):
        pass

    def complete(self):
        pass

    def first_time_init(self, jarvis):
        remind_still_active = []
        for item in self.get_data(jarvis):
            timestamp = item['timestamp']
            if timestamp < time.time():
                time_format = self.timestamp_to_string(timestamp)
                jarvis.say(
                    "Reminder: {} missed ({})".format(
                        item['message'], time_format), Fore.MAGENTA)
                continue

            schedule_id = jarvis.schedule(timestamp, self.reminder_exec,
                                          item['message'])
            item['schedule_id'] = schedule_id
            remind_still_active += [item]
        self.save_data(jarvis, remind_still_active)

    def add(self, jarvis, message, timestamp=None, schedule_id=None):
        data = self.get_data(jarvis)
        next_id = self.get_next_id(jarvis)
        new_entry = {
            'message': message,
            'timestamp': timestamp,
            'schedule_id': schedule_id,
            'id': next_id
        }
        new_data = data + [new_entry]
        self.save_data(jarvis, new_data)

    def clean_up_entry(self, jarvis, entry):
        jarvis.cancel(entry['schedule_id'])

    def format(self, entry):
        time = self.timestamp_to_string(entry['timestamp'])
        return "{} => {}".format(time, entry['message'])

    def sort(self, remind_list):
        return sorted(remind_list, key=lambda entry: entry['timestamp'])

    def reminder_exec(self, jarvis, schedule_id, message):
        jarvis.notification(message)

        data = self.get_data(jarvis)
        data = [entry for entry in data if entry['schedule_id'] != schedule_id]
        self.save_data(jarvis, data)

    def timestamp_to_string(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime("%H:%M:%S")

    def parse_date_timestamp(self, date):
        date = parse_date(date)
        if date[0] == 0:
            return None
        timestamp = time.mktime(date[1].timetuple())
        return timestamp - time.time()

    def remind_add(self, jarvis, s, time_in_parser, example):
        s = s.split("to")
        if len(s) != 2:
            jarvis.say("Sorry, please say something like:", Fore.MAGENTA)
            jarvis.say(" > {}".format(example), Fore.MAGENTA)
            return

        time_in = time_in_parser(s[0])
        while time_in is None:
            jarvis.say("Sorry, when should I remind you?", Fore.MAGENTA)
            time_in = timeparse(input("Time: "))
        timestamp = time.time() + time_in

        message = s[1]

        # schedule
        schedule_id = jarvis.schedule(timestamp - time.time(),
                                      self.reminder_exec, message)
        self.add(jarvis, message, timestamp=timestamp, schedule_id=schedule_id)


############# PLUGIN DEFINITION ##########################
class Todo(Plugin, TodoBase):
    """List todo list"""

    def run(self, jarvis, s):
        self.print(jarvis)


class Todo_Add(Plugin, TodoBase):
    """Add new todo entry"""

    def run(self, jarvis, s):
        self.add(jarvis, s)


class Todo_Remove(Plugin, TodoBase):
    """
    Remove reminder
    -- Example:
        remove
        remove everything
    """

    def run(self, jarvis, s):
        self.remove(jarvis, s)


class Remind(Plugin, RemindBase):
    """List all scheduled reminders"""

    def init(self, jarvis):
        self.first_time_init(jarvis)

    def run(self, jarvis, s):
        jarvis.say("## {} ##\n".format(self.timestamp_to_string(time.time())))
        self.print(jarvis)


class Remind_At(Plugin, RemindBase):
    """
    Add reminder
    -- Example:
        Remind at 12:30 to XXX
    """

    def run(self, jarvis, s):
        self.remind_add(jarvis, s, self.parse_date_timestamp,
                        'remind at 12:30 to XXX')


class Remind_In(Plugin, RemindBase):
    """
    Add reminder
    -- Example:
        remind in 30 minutes 10 seconds to XXX
    """


    def run(self, jarvis, s):
        self.remind_add(jarvis, s, timeparse, 'remind in 30m 10s to XXX')


class Remind_Remove(Plugin, RemindBase):
    """
    -- Example:
        remove
        remove everything
    """

    def run(self, jarvis, s):
        self.remove(jarvis, s)
