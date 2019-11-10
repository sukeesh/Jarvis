import signal
from cmd import Cmd
from functools import partial
import sys
import traceback

from colorama import Fore
from PluginManager import PluginManager

from utilities import schedule
from utilities.voice import create_voice
from utilities.notification import notify
from utilities.GeneralUtilities import print_say

from packages.memory.memory import Memory
from utilities.animations import SpinnerThread


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
        self.spinner_running = False

    def say(self, text, color="", speak=True):
        """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
        :param color: for text - use colorama (https://pypi.org/project/colorama/)
                      e.g. Fore.BLUE
        :param speak: False-, if text shouldn't be spoken even if speech is enabled
        """
        print(color + text + Fore.RESET)
        if speak:
            self._jarvis.speak(text)

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
                    prompt = "Sorry, needs to be between {} and {}. Try again: ".format(rmin, rmax)
                else:
                    return value
            except ValueError:
                prompt = 'Sorry, needs to be a number. Try again: '
                continue

    def connection_error(self):
        """Print generic connection error"""

        if self.is_spinner_running():
            self.spinner_stop('')

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
        spinner = SpinnerThread('Cancelling', 0.15)
        spinner.start()

        self._jarvis.scheduler.cancel(schedule_id)

        spinner.stop()
        jarvis.say('Cancellation successful', Fore.GREEN)

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

    def spinner_start(self, message="Starting "):
        """
        Function for starting a spinner when prompted from a plugin
        and a default message for performing the task
        """
        self.spinner_running = True
        self.spinner = SpinnerThread(message, 0.15)
        self.spinner.start()

    def spinner_stop(self, message="Task executed successfully! ", color=Fore.GREEN):
        """
        Function for stopping the spinner when prompted from a plugin
        and displaying the message after completing the task
        """
        self.spinner.stop()
        self.say(message, color)
        self.spinner_running = False

    def is_spinner_running(self):
        return self.spinner_running


def catch_all_exceptions(do, pass_self=True):
    def try_do(self, s):
        try:
            if pass_self:
                do(self, s)
            else:
                do(s)
        except Exception:
            if self.is_spinner_running():
                self.spinner_stop("It seems some error has occured")
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
        # what if the platform does not have any engines, travis doesn't have sapi5 acc to me
        try:
            self.speech = create_voice()
        except Exception as e:
            print_say("Voice not supported", self, Fore.RED)
            print_say(str(e), self, Fore.RED)

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

        '''Stop the spinner if it is already running'''
        if self._api.is_spinner_running():
            self._api.spinner_stop('Some error has occured')

        print_say("Goodbye, see you later!", self, Fore.RED)
        self.scheduler.stop_all()
        sys.exit()

    def execute_once(self, command):
        self.get_api().eval(command)
        self.close()

    def error(self):
        """Jarvis let you know if an error has occurred."""
        print_say("I could not identify your command...", self, Fore.RED)

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
                        " OR ".join(reason)),
                    self)

    def help_status(self):
        print_say("Prints info about enabled or disabled plugins", self)
        print_say("Use \"status short\" to omit detailed information.", self)
