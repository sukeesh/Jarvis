import tempfile
import threading
from cmd import Cmd
from threading import Semaphore
from typing import Dict, Optional

from colorama import Fore

import frontend.cmd_interpreter
import frontend.gui.jarvis_gui
import frontend.server.server
import frontend.voice
import frontend.voice_control
from packages.memory.memory import Memory
from plugin import Plugin
from utilities import schedule
from utilities.GeneralUtilities import warning
from utilities.notification import notify

# register hist path via tempfile
HISTORY_FILENAME = tempfile.TemporaryFile('w+t')


class Jarvis:
    _CONNECTION_ERROR_MSG = "It seems like I'm not connected to the Internet. Check your connection and try again!"

    AVAILABLE_FRONTENDS = {'cli': frontend.cmd_interpreter.CmdInterpreter,
                           'gui': frontend.gui.jarvis_gui.JarvisGui,
                           'server': frontend.server.server.JarvisServer,
                           'voice': frontend.voice.JarvisVoice,
                           'voice_control': frontend.voice_control.VoiceControl
                           }

    def __init__(self, language_parser, plugin_manager):
        self.language_parser = language_parser
        self.plugin_manager = plugin_manager

        self.plugins = self.plugin_manager.get_plugins()
        self.language_parser.train(self.plugins.values())

        self.cache = ''
        self.stdout = self

        self.spinner_running = False

        self.memory = Memory()
        self.scheduler = schedule.Scheduler()

        self.active_frontends = {}
        self.running = Semaphore()

        for plugin in self.plugins.values():
            plugin.init(self)

    def activate_frontend(self, frontend):
        if frontend not in self.active_frontends:
            _f = self.AVAILABLE_FRONTENDS[frontend](self)
            self.active_frontends[frontend] = _f
            _f.thread = threading.Thread(target=_f.start)
            if self.running._value == 0:
                _f.thread.start()

    def disable_frontend(self, frontend):
        if frontend in self.active_frontends:
            if self.spinner_running:
                self.active_frontends[frontend].spinner_stop()
            self.active_frontends[frontend].stop()
            thread = self.active_frontends[frontend].thread
            del self.active_frontends[frontend]
            return thread

    def frontend_info(self):
        frontend_status_formatter = {
            "available": len(self.AVAILABLE_FRONTENDS),
            "active": len(self.active_frontends),
            "red": Fore.RED,
            "blue": Fore.BLUE,
            "reset": Fore.RESET
        }

        frontend_status = "Jarvis can only be active on {active} frontends for now.\n" \
                          "We are working on getting the other frontends working.\n"

        frontend_status += "{red}{active} {blue}frontends loaded of" \
                           " {red}{available} {blue}frontends. More information: {red}status\n"
        frontend_status += Fore.RESET

        return frontend_status.format(**frontend_status_formatter)

    def run(self):
        for _frontend in self.active_frontends.values():
            _frontend.thread.start()
        self._prompt()

        self.running.acquire()

        # Stop Jarvis -> release self.running
        # exit-code should be executed from main thread
        # to avoid strange behaviour

        self.running.acquire()

        self.say("Goodbye, see you later!", Fore.RED)
        self.scheduler.stop_all()

        for _frontend_name in [x for x in self.active_frontends.keys()]:
            print('Stopping {}'.format(_frontend_name))
            self.disable_frontend(_frontend_name).join()

        import sys
        sys.exit(0)

    def get_plugins(self):
        return self.plugins

    def say(self, text, color="", speak=True):
        """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
        :param color: for text - use colorama (https://pypi.org/project/colorama/)
                      e.g. Fore.BLUE
        :param speak: False-, if text shouldn't be spoken even if speech is enabled
        """
        for _frontend in self.active_frontends.values():
            _frontend.say(text, color)

    def input(self, prompt="", color="", password=False):
        """
        Get user input
        """
        for _frontend in self.active_frontends.values():
            return _frontend.input(prompt, color, password)

    def exit(self):
        """Immediately exit Jarvis"""
        print('EXIT IMMEDIATELY')
        self.running.release()

    def _speak(self, text):
        if self.enable_voice:
            self.speech.text_to_speech(text)

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

        self.say(self._CONNECTION_ERROR_MSG)

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
        return self.scheduler.create_event(
            time_seconds, function, self, *args)

    def cancel(self, schedule_id):
        """
        Cancel event scheduled with schedule
        :param schedule_id: id returned by schedule
        """
        self.scheduler.cancel(schedule_id)
        self.say('Cancellation successful', Fore.GREEN)

    # MEMORY WRAPPER
    def get_data(self, key):
        """
        Get a specific key from memory
        """
        return self.memory.get_data(key)

    def add_data(self, key, value):
        """
        Add a key and value to memory
        """
        self.memory.add_data(key, value)
        self.memory.save()

    def update_data(self, key, value):
        """
        Updates a key with supplied value.
        """
        self.memory.update_data(key, value)
        self.memory.save()

    def del_data(self, key):
        """
        Delete a key from memory
        """
        self.memory.del_data(key)
        self.memory.save()

    def spinner_start(self, message="Starting "):
        """
        Function for starting a spinner when prompted from a plugin
        and a default message for performing the task
        """
        self.spinner_running = True
        for _frontend in self.active_frontends.values():
            _frontend.spinner_start(message)

    def spinner_stop(self, message="Task executed successfully! ", color=Fore.GREEN):
        """
        Function for stopping the spinner when prompted from a plugin
        and displaying the message after completing the task
        """
        self.spinner_running = False
        for _frontend in self.active_frontends.values():
            _frontend.spinner_stop(message)

    def is_spinner_running(self):
        return self.spinner_running

    def plugin_info(self):
        plugin_status_formatter = {
            "disabled": len(self.plugin_manager.get_disabled()),
            "enabled": self.plugin_manager.get_number_plugins_loaded(),
            "red": Fore.RED,
            "blue": Fore.BLUE,
            "reset": Fore.RESET
        }

        plugin_status = "{red}{enabled} {blue}plugins loaded"
        if plugin_status_formatter['disabled'] > 0:
            plugin_status += " {red}{disabled} {blue}plugins disabled. More information: {red}status\n"
        plugin_status += Fore.RESET

        return plugin_status.format(**plugin_status_formatter)

    def execute_once(self, command: str) -> Optional[bool]:
        # save commands' history
        HISTORY_FILENAME.write(command + '\n')

        plugin = self.language_parser.identify_action(command)

        if command.startswith('help'):
            self.do_help(plugin)
            return True

        if plugin is None:
            return None

        s = self._build_s_string(command, plugin)
        ret = plugin.run(self, s)

        if ret is False:
            self.say("I could not identify your command...", Fore.RED)
        self._prompt()

    def _prompt(self):
        for _f in self.active_frontends.values():
            _f.show_prompt()

    def _build_s_string(self, data: str, plugin: Plugin):
        features = self._parse_plugin_features(plugin.feature())

        if not features['punctuation']:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(",", "")

        if not features['case_sensitive']:
            data = data.lower()

        data = data.replace(plugin.get_name(), '')
        for alias in plugin.alias():
            data = data.replace(alias, '')
        data = data.strip()
        data = " ".join(data.split())
        return data

    def _parse_plugin_features(self, features_iter):
        plugin_features = {
            "case_sensitive": False,
            "punctuation": True
        }

        if features_iter is None:
            return plugin_features

        for feature in features_iter:
            key = feature[0]
            value = feature[1]

            if not isinstance(value, bool):
                warning("{}={}: No supported requirement".format(key, value))

            if key in plugin_features:
                plugin_features[key] = value
            else:
                warning("{}={}: No supported requirement".format(key, value))

        return plugin_features

    def do_help(self, plugin: Optional[Plugin]):
        if plugin is not None:
            self.say(plugin.get_doc())
        else:
            self.say("")
            headerString = "These are valid commands for Jarvis"
            formatString = "Format: command ([aliases for command])"
            self.say(headerString)
            self.say(formatString, Fore.BLUE)
            pluginDict = self.plugin_manager.get_plugins()
            uniquePlugins: Dict[str, Plugin] = {}
            for key in pluginDict.keys():
                plugin = pluginDict[key]
                if (plugin not in uniquePlugins.keys()):
                    uniquePlugins[plugin.get_name()] = plugin
            helpOutput = []
            for name in sorted(uniquePlugins.keys()):
                if (name == "help"):
                    continue
                try:
                    aliasString = ", ".join(uniquePlugins[name].alias())
                    if (aliasString != ""):
                        pluginOutput = "* " + name + " (" + aliasString + ")"
                        helpOutput.append(pluginOutput)
                    else:
                        helpOutput.append("* " + name)
                except AttributeError:
                    helpOutput.append("* " + name)

            Cmd.columnize(self, helpOutput, displaywidth=100)

    def write(self, line):
        if line.endswith('\n'):
            self.say(self.cache + line[:-1])
            self.cache = ''
        else:
            self.cache += line
