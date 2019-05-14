import signal
from cmd import Cmd
from functools import partial
import traceback
import sys

from colorama import Fore
from PluginManager import PluginManager

from utilities import schedule
from utilities.voice import create_voice
from utilities.notification import notify
from utilities.GeneralUtilities import print_say

from packages.memory.memory import Memory


class JarvisAPI(object):
    """
    Jarvis interface for plugins.

    Plugins will receive a instance of this as the second (non-self) parameter
    of the exec()-method.

    Everything Jarvis-related that can't be implemented as a stateless-function
    in the utilities-package should be implemented here.
    """

    _CONNECTION_ERROR_MSG = "You are not connected to Internet"

    def __init__(self, jarvis):
        self._jarvis = jarvis

    def say(self, text, color=""):
        """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
        :param color: for text - use colorama (https://pypi.org/project/colorama/)
                      e.g. Fore.BLUE
        """
        self._jarvis.speak(text)
        print(color + text + Fore.RESET)

    def input(self, prompt="", color=""):
        """
        Get user input
        """
        # we can't use input because for some reason input() and color codes do not work on
        # windows cmd
        sys.stdout.write(color + prompt + Fore.RESET)
        sys.stdout.flush()
        text = sys.stdin.readline()
        # return without newline
        return text.rstrip()

    def input_number(self, prompt="", color="", rtype=float, rmin=None, rmax=None):
        """
        Get user input: As number.

        Guaranteed only returns number - ask user till correct number entered.

        :param prompt: Printed to console
        :param color: Color of prompot
        :param rtype: type of return value; e.g. float (default) or int
        :param rmin: Minum of values returned
        :param rmax: Maximum of values returned
        """
        while True:
            try:
                value = rtype(self.input(prompt, color).replace(',', '.'))
                if (rmin is not None and value < rmin) or (rmax is not None and value > rmax):
                    prompt = "Sorry, needs to be between {} and {}. Try again: ".format(rmin, ramx)
                else:
                    return value
            except ValueError:
                prompt = 'Sorry, needs to be a number. Try again: '
                continue

    def connection_error(self):
        """Print generic connection error"""
        self.say(JarvisAPI._CONNECTION_ERROR_MSG)

    def exit(self):
        """Immediately exit Jarvis"""
        self._jarvis.close()

    def notification(self, msg, time_seconds=0):
        """
        Sends notification msg in time_in milliseconds
        :param msg: Message. Either String (message body) or tuple (headline, message body)
        :param time_seconds: Time in seconds to wait before showing notification
        """
        if isinstance(msg, tuple):
            headline, message = msg
        elif isinstance(msg, str):
            headline = "Jarvis"
            message = msg
        else:
            raise ValueError("msg not a string or tuple")

        if time_seconds == 0:
            notify(headline, message)
        else:
            schedule(time_seconds, notify, headline, message)

    def schedule(self, time_seconds, function, *args):
        """
        Schedules function
        After time_seconds call function with these parameter:
           - reference to this JarvisAPI instance
           - schedule_id (return value of this function)
           - *args
        :return: integer, id - use with cancel
        """
        return self._jarvis.scheduler.create_event(
            time_seconds, function, self, *args)

    def cancel(self, schedule_id):
        """
        Cancel event scheduled with schedule
        :param schedule_id: id returned by schedule
        """
        self._jarvis.scheduler.cancel(schedule_id)

    # Voice wrapper
    def enable_voice(self):
        """
        Use text to speech for every text passed to jarvis.say()
        """
        self._jarvis.enable_voice = True

    def disable_voice(self):
        """
        Stop text to speech output for every text passed to jarvis.say()
        """
        self._jarvis.enable_voice = False

    def is_voice_enabled(self):
        """
        Returns True/False if voice is enabled/disabled with
        enable_voice or disable_voice
        Default: False (disabled)
        """
        return self._jarvis.enable_voice

    # MEMORY WRAPPER
    def get_data(self, key):
        """
        Get a specific key from memory
        """
        return self._jarvis.memory.get_data(key)

    def add_data(self, key, value):
        """
        Add a key and value to memory
        """
        self._jarvis.memory.add_data(key, value)
        self._jarvis.memory.save()

    def update_data(self, key, value):
        """
        Updates a key with supplied value.
        """
        self._jarvis.memory.update_data(key, value)
        self._jarvis.memory.save()

    def del_data(self, key):
        """
        Delete a key from memory
        """
        self._jarvis.memory.del_data(key)
        self._jarvis.memory.save()

    def eval(self, s):
        """
        Simulates typing 's' in Jarvis prompt
        """
        line = self._jarvis.precmd(s)
        stop = self._jarvis.onecmd(line)
        stop = self._jarvis.postcmd(stop, line)


def catch_all_exceptions(do, pass_self=True):
    def try_do(self, s):
        try:
            if pass_self:
                do(self, s)
            else:
                do(s)
        except Exception:
            print(
                Fore.RED
                + "Some error occurred, please open an issue on github!")
            print("Here is error:")
            print('')
            traceback.print_exc()
            print(Fore.RESET)
    return try_do


class CmdInterpreter(Cmd):
    # We use this variable at Breakpoint #1.
    # We use this in order to allow Jarvis say "Hi", only at the first
    # interaction.

    # This can be used to store user specific data

    def __init__(
            self,
            first_reaction_text,
            prompt,
            directories=[],
            first_reaction=True,
            enable_voice=False):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        Cmd.__init__(self)
        self.first_reaction = first_reaction
        self.first_reaction_text = first_reaction_text
        self.prompt = prompt
        self.enable_voice = enable_voice
        # Register do_quit() function to SIGINT signal (Ctrl-C)
        signal.signal(signal.SIGINT, self.interrupt_handler)

        self.memory = Memory()
        self.scheduler = schedule.Scheduler()
        self.speech = create_voice()

        self.fixed_responses = {"what time is it": "clock",
                                "where am i": "pinpoint",
                                }

        self._api = JarvisAPI(self)
        self._plugin_manager = PluginManager()

        for directory in directories:
            self._plugin_manager.add_directory(directory)

        self._activate_plugins()
        self._init_plugin_info()

    def _init_plugin_info(self):
        plugin_status_formatter = {
            "disabled": len(self._plugin_manager.get_disabled()),
            "enabled": self._plugin_manager.get_number_plugins_loaded(),
            "red": Fore.RED,
            "blue": Fore.BLUE,
            "reset": Fore.RESET
        }

        plugin_status = "{red}{enabled} {blue}plugins loaded"
        if plugin_status_formatter['disabled'] > 0:
            plugin_status += " {red}{disabled} {blue}plugins disabled. More information: {red}status\n"
        plugin_status += Fore.RESET

        self.first_reaction_text += plugin_status.format(
            **plugin_status_formatter)

    def _activate_plugins(self):
        """Generate do_XXX, help_XXX and (optionally) complete_XXX functions"""
        for (plugin_name, plugin) in self._plugin_manager.get_plugins().items():
            self._plugin_update_completion(plugin, plugin_name)

            run_catch = catch_all_exceptions(plugin.run)
            setattr(
                CmdInterpreter,
                "do_"
                + plugin_name,
                partial(
                    run_catch,
                    self))
            setattr(
                CmdInterpreter,
                "help_" + plugin_name,
                partial(
                    self._api.say,
                    plugin.get_doc()))

            plugin.init(self._api)

    def _plugin_update_completion(self, plugin, plugin_name):
        """Return True if completion is available"""
        completions = [i for i in plugin.complete()]
        if len(completions) > 0:
            def complete(completions):
                def _complete_impl(self, text, line, begidx, endidx):
                    return [i for i in completions if i.startswith(text)]
                return _complete_impl
            setattr(
                CmdInterpreter,
                "complete_"
                + plugin_name,
                complete(completions))

    def get_api(self):
        return self._api

    def close(self):
        """Closing Jarvis."""
        print_say("Goodbye, see you later!", self, Fore.RED)
        self.scheduler.stop_all()
        exit()

    def completedefault(self, text, line, begidx, endidx):
        """Default completion"""
        return [i for i in self.actions if i.startswith(text)]

    def error(self):
        """Jarvis let you know if an error has occurred."""
        print_say("I could not identify your command...", self, Fore.RED)

    def get_completions(self, command, text):
        """Returns a list with the completions of a command."""
        dict_target = [item for item in self.actions
                       if isinstance(item, dict) and command in item][0]
        completions_list = dict_target[command]
        return [i for i in completions_list if i.startswith(text) and i != '']

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        self.close()

    def do_status(self, s):
        """Prints plugin status status"""
        count_enabled = self._plugin_manager.get_number_plugins_loaded()
        count_disabled = len(self._plugin_manager.get_disabled())
        print_say(
            "{} Plugins enabled, {} Plugins disabled.".format(
                count_enabled,
                count_disabled),
            self)

        if "short" not in s and count_disabled > 0:
            print_say("", self)
            for disabled, reason in self._plugin_manager.get_disabled().items():
                print_say(
                    "{:<20}: {}".format(
                        disabled,
                        "OR ".join(reason)),
                    self)

    def help_status(self):
        print_say("Prints info about enabled or disabled plugins", self)
        print_say("Use \"status short\" to omit detailed information.", self)
