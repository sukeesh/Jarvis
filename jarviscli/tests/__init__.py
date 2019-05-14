import unittest
from functools import partial
from CmdInterpreter import JarvisAPI


class MockJarvisAPI(JarvisAPI):
    def __init__(self):
        self.call_history = MockHistoryBuilder().\
            add_field('operation').\
            add_field('args').\
            add_field('return').\
            build()

        self.say_history = MockHistoryBuilder().\
            add_field('text').\
            add_field('color').\
            build()

        self.notification_history = MockHistoryBuilder().\
            add_field('msg').\
            add_field('time_seconds').\
            build()

        self.schedule_history = MockHistoryBuilder().\
            add_field('time_seconds').\
            add_field('function').\
            add_field('args').\
            build()

        self.data = {}
        self._input_queue = []
        self.is_voice_enabled = False

    def say(self, text, color=""):
        # remove \n
        text = text.rstrip('\n')
        self.say_history.record(text, color)
        self.call_history.record('say', (text, color), None)

    def queue_input(self, text):
        self._input_queue.append(text)

    def input(self, prompt='', color=''):
        if len(self._input_queue) == 0:
            raise BaseException("MockJarvisAPI: No predefined answer in queue - add answer with 'self.queue_input(\"TEXT\")'")
        return self._input_queue.pop()

    def input_number(self, prompt='', color='', rtype=float, rmin=None, rmax=None):
        return JarvisAPI.input_number(self, prompt, color, rtype, rmin, rmax)

    def connection_error(self):
        self.call_history.record('connection_error', (), None)

    def exit(self):
        self.call_history.record('exit', (), None)

    def notification(self, msg, time_seconds=0):
        self.notification_history.record(msg, time_seconds)
        self.call_history.record('notification', (msg, time_seconds), None)

    def schedule(self, time_seconds, function, *args):
        self.notification_history.record(time_seconds, function, *args)
        self.call_history.record(
            'schedule', (time_seconds, function, args), None)

    def cancel(self, schedule_id):
        self.call_history.record('cancel', (), None)

    def enable_voice(self):
        self.call_history.record('enable_voice', (), None)
        self.is_voice_enabled = True

    def disable_voice(self):
        self.call_history.record('disable_voice', (), None)
        self.is_voice_enabled = False

    def is_voice_enabled(self):
        self.call_history.record('is_voice_enabled', (), self.is_voice_enabled)
        return self.is_voice_enabled

    def get_data(self, key):
        if key not in self.data:
            value = None
        else:
            value = self.data[key]
        self.call_history.record('get_data', (key), value)
        return value

    def add_data(self, key, value):
        self.data[key] = value
        self.call_history.record('add_data', (key, value), None)

    def update_data(self, key, value):
        self.data[key] = value
        self.call_history.record('update_data', (key, value), None)

    def del_data(self, key):
        del self.data[key]
        self.call_history.record('del_data', (key), None)

    def eval(self, s):
        self.call_history.record('eval', s)


class MockHistoryBuilder():
    def __init__(self):
        self._history = MockHistory()

    def add_field(self, field):
        self._history._storage_by_field[field] = []
        self._history.__dict__[
            'contains_{}'.format(field)] = partial(
            self._history.contains, field)
        self._history.__dict__[
            'view_{}'.format(field)] = partial(
            self._history.view, field)
        self._history.__dict__[
            'last_{}'.format(field)] = partial(
            self._history.last, field)
        self._history._field_list.append(field)
        return self

    def build(self):
        return self._history


class MockHistory():
    """
    Record/Output history.

    Recorded data sets must contain fixed and predefined number of "fields" (e.g. text and color).

    Note: For Methods with first parameter "field" method "name_field" exist.
    So "view('text')" can be rewritten as "view_text".
    """

    def __init__(self):
        self._storage_by_field = {}
        self._storage_by_index = []

        self._field_list = []
        self._counter = 0

    def record(self, *args):
        """
        Do not call manually!
        """
        if len(self._field_list) != len(args):
            raise ValueError(
                "Argument count miss-match: {} --- {}".format(self._field_list, args))
        for i, field in enumerate(self._field_list):
            self._storage_by_field[field].append(args[i])
        self._storage_by_index.append(args)
        self._counter += 1

    def contains(self, field=None, value=None):
        """
        Check if value is recorded.
        If field is None, value should be a tuple of values
        for all fields.
        """
        if field is None:
            return value in self._storage_by_index
        else:
            return value in self._storage_by_field[field]

    def view(self, field=None, index=None):
        """
        Returns value.

        If field is None, returns tuple of all values for all fields.
        If index is None, returns all recorded values
        """
        if field is None:
            if index is None:
                return self._storage_by_index
            else:
                return self._storage_by_index[index]
        else:
            if index is None:
                return self._storage_by_field[field]
            else:
                return self._storage_by_field[field][index]

    def last(self, field=None):
        """Shortcut for view with index -1"""
        return self.view(field, -1)

    def get_length(self):
        """Returns how many data sets were recorded"""
        return self._counter


class PluginTest(unittest.TestCase):
    def setUp(self):
        self._setUp()

    def _setUp(self):
        if 'jarvis_api' not in self.__dict__ or self.jarvis_api is None:
            self.jarvis_api = MockJarvisAPI()

    def load_plugin(self, plugin_class):
        """
        Returns Plugin Instance (object).
        Works for both callable classes or methods.

        Adds method run(string) - which execute plugin using mocked api.
        """
        self._setUp()

        plugin_backend = plugin_class()._backend[0]
        plugin_backend.run = partial(plugin_backend, self.jarvis_api)
        return plugin_backend

    def tearDown(self):
        self.jarvis_api = None

    def queue_input(self, msg):
        """
        Queue msg to be returned by 'jarvis.input()'
        """
        self.jarvis_api.queue_input(msg)

    def histroy_call(self):
        """
        Returns MockHistory instance. Fields:

        1. operation (string)
        2. args (tuple)
        3. return value
        """
        return self.jarvis_api.call_history

    def history_say(self):
        """
        Returns MockHistory instance. Fields:

        1. text (string)
        2. color (colorama.Fore.*)
        """
        return self.jarvis_api.say_history

    def history_notification(self):
        """
        Returns MockHistory instance. Fields:

        1. msg (string)
        2. time_seconds (int)
        """
        return self.jarvis_api.notification_history

    def history_schedule(self):
        """
        Returns MockHistory instance. Fields:

        1. time_seconds (int)
        2. function
        3. args (tuple)
        """
        return self.jarvis_api.schedule_history
