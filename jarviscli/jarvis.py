import os
import tempfile
import threading
import traceback
from cmd import Cmd
from threading import Semaphore
from typing import Dict, Optional

from colorama import Fore

import frontend.cli.cmd_interpreter
import frontend.gui.jarvis_gui
import frontend.server.server
import frontend.voice
import frontend.voice_control
from packages.memory.key_vault import KeyVault
from packages.memory.memory import Memory
from packages.notification import (NOTIFY_CRITICAL, NOTIFY_LOW, NOTIFY_NORMAL,
                                   notify)
from packages.online_status import OnlineStatus
from packages.schedule import Scheduler
from plugin import Plugin
from utilities.GeneralUtilities import warning

# register hist path via tempfile
HISTORY_FILENAME = tempfile.TemporaryFile('w+t')


class Jarvis:
    _CONNECTION_ERROR_MSG = "It seems like I'm not connected to the Internet. Check your connection and type 'connect'!"

    AVAILABLE_FRONTENDS = {'cli': frontend.cli.cmd_interpreter.CmdInterpreter,
                           'gui': frontend.gui.jarvis_gui.JarvisGui,
                           'server': frontend.server.server.JarvisServer,
                           'tts': frontend.voice.JarvisVoice,
                           'voice_control': frontend.voice_control.VoiceControl
                           }

    NOTIFY_LOW = NOTIFY_LOW
    NOTIFY_NORMAL = NOTIFY_NORMAL
    NOTIFY_CRITICAL = NOTIFY_CRITICAL

    def __init__(self, language_parser_class, plugin_manager):
        self._data_dir = os.path.join(os.path.dirname(__file__), 'data')

        self.cache = ''
        self.stdout = self

        self.spinner_running = False

        self.memory = Memory()
        self.key_vault = KeyVault()
        self.scheduler = Scheduler()

        self.active_frontends = {}
        self.running = Semaphore()

        self.online_status = OnlineStatus()
        self.offline_only = False
        self.plugins_offline = {}
        self.plugins_online = {}

        self.plugin_manager = plugin_manager
        self.plugin_manager.set_key_vault(self.key_vault)
        self.plugins = self.plugin_manager.get_plugins()

        for name, plugin in self.plugins.items():
            # plugin.run = catch_all_exceptions(plugin.run)
            try:
                plugin.init(self)
            except Exception as e:
                print("Failed init plugin")
                print(e)
                traceback.print_exc()

            if plugin.require().network:
                self.plugins_online[name] = plugin
            else:
                self.plugins_offline[name] = plugin

        self.language_parser_online = language_parser_class()
        self.language_parser_online.train(self.plugins.values())
        self.language_parser_offline = language_parser_class()
        self.language_parser_offline.train(self.plugins_offline.values())

    def set_offline_mode(self, state=True):
        self.offline_only = True

    def get_plugins(self):
        if not self.offline_only and self.online_status.get_online_status():
            return self.plugins
        else:
            return self.plugins_offline

    def get_language_parser(self):
        if not self.offline_only and self.online_status.get_online_status():
            return self.language_parser_online
        else:
            return self.language_parser_offline

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

        self.online_status.refresh()

        if self.is_spinner_running():
            self.spinner_stop('')

        self.say(self._CONNECTION_ERROR_MSG)

    def notification(self, msg, time_seconds=0, urgency=NOTIFY_NORMAL):
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
            self.schedule(time_seconds, notify, headline, message)

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

    # KEY VAULT WRAPPER
    def save_user_pass(self, key, user, password):
        """
        Saves the username and password combination
        """
        self.key_vault.save_user_pass(key, user, password)
        self.key_vault.save()

    def update_user_pass(self, key, user, password):
        """
        Updates the username and password combination
        """
        self.key_vault.update_user_pass(key, user, password)
        self.key_vault.save()

    def get_user_pass(self, key):
        """
        Gets the username and password combination
        """
        return self.key_vault.get_user_pass(key)

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

    def data_file(self, *path):
        return os.path.join(self._data_dir, *path)

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

    def eval(self, command: str) -> Optional[bool]:
        # save commands' history
        HISTORY_FILENAME.write(command + '\n')

        plugin = self.get_language_parser().identify_action(command)

        if command.startswith('help'):
            self.do_help(plugin)
        elif plugin is None:
            self.say("I could not identify your command...", Fore.RED)
        else:
            s = self._build_s_string(command, plugin)
            call_args = {}
            for api_key in plugin.require().api_keys:
                call_args[api_key] = self.get_user_pass(api_key)[1]

            plugin.run(self, s, **call_args)

    def execute_once(self, command: str) -> Optional[bool]:
        self.eval(command)
        self._prompt()

    def internal_execute(self, command: str, s: str, **kwargs):
        # save commands' history
        HISTORY_FILENAME.write(command + '\n')

        plugin = self.get_language_parser().identify_action(command)

        if command.startswith('help'):
            self.do_help(plugin)
            return True

        if plugin is None:
            return None

        return plugin.internal_execute(self, s)

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
            pluginDict = self.get_plugins()
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


def catch_all_exceptions(do, pass_self=True):
    def try_do(self, s, **args):
        try:
            if pass_self:
                do(self, s, **args)
            else:
                do(s, **args)
        # except ConnectionError:
        #    # TODO GO OFFLINE
        #    pass
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
