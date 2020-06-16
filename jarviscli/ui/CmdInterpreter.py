import signal
import sys
import traceback
from cmd import Cmd

import colorama
from colorama import Fore

PROMPT_CHAR = '~>'


class CmdInterpreterJarvisAPI():
    def __init__(self, cmd_interpreter):
        super().__init__()
        self.cmd_interpreter = cmd_interpreter

    def say(self, text, color=''):
        print(color + text + Fore.RESET, flush=True)

    def input(self, prompt="", color=""):
        # we can't use input because for some reason input() and color codes do not work on
        # windows cmd
        sys.stdout.write(color + prompt + Fore.RESET)
        sys.stdout.flush()
        text = sys.stdin.readline()
        # return without newline
        return text.rstrip()

    def exit(self):
        self.cmd_interpreter.close()


class CmdInterpreter(Cmd):

    first_reaction_text = """\
{BLUE}Jarvis' sound is by default disabled.{RESET}
{BLUE}In order to let Jarvis talk out load type:{RESET}{RED}enable sound{RESET}
Type 'help' for a list of available actions.
""".format(BLUE=Fore.BLUE, RESET=Fore.RESET, RED=Fore.RED)

    prompt = (
        Fore.RED
        + "{} Hi, what can I do for you?\n".format(PROMPT_CHAR)
        + Fore.RESET)

    def __init__(self, jarvis):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        super().__init__()

        self._jarvis = jarvis
        _api_io = CmdInterpreterJarvisAPI(self)
        self._api = self._jarvis.register_io(_api_io)

        # enable color on windows
        colorama.init()
        # change raw input based on os
        if sys.platform == 'win32':
            self.use_rawinput = False

        self.first_reaction = True

        # Register do_quit() function to SIGINT signal (Ctrl-C)
        signal.signal(signal.SIGINT, self.interrupt_handler)
        self.first_reaction_text += self._jarvis.plugin_info()

        for plugin in self._jarvis.activate_plugins():
            self._add_plugin(plugin)

        self._api.say(self.first_reaction_text)

    def _add_plugin(self, plugin):
        plugin.run = catch_all_exceptions(plugin.run)

        completions = [i for i in plugin.complete()]
        if len(completions) > 0:
            def complete(completions):
                def _complete_impl(self, text, line, begidx, endidx):
                    return [i for i in completions if i.startswith(text)]
                return _complete_impl
            setattr(
                CmdInterpreter,
                "complete_"
                + plugin.get_name(),
                complete(completions))

    def close(self):
        """Closing Jarvis."""

        '''Stop the spinner if it is already running'''
        if self._api.is_spinner_running():
            self._api.spinner_stop('Some error has occured')

        self._api.say("Goodbye, see you later!", Fore.RED)
        self._api.scheduler.stop_all()
        sys.exit()

    def precmd(self, line: str) -> str:
        return line

    def onecmd(self, s: str):
        result = self._jarvis.execute_once(s)
        if result is None:
            self.error()

    def postcmd(self, stop, line):
        """Hook that executes after every command."""
        if self.first_reaction:
            self.prompt = (
                Fore.RED
                + "{} What can I do for you?\n".format(PROMPT_CHAR)
                + Fore.RESET)
            self.first_reaction = False
        self._api._speak("What can I do for you?\n")

    def error(self):
        """Jarvis let you know if an error has occurred."""
        self._api.say("I could not identify your command...", Fore.RED)

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        self.close()

    def do_status(self, s):
        """Prints plugin status status"""
        count_enabled = self._plugin_manager.get_number_plugins_loaded()
        count_disabled = len(self._plugin_manager.get_disabled())
        self._api.say(
            "{} Plugins enabled, {} Plugins disabled.".format(
                count_enabled,
                count_disabled),
            self)

        if "short" not in s and count_disabled > 0:
            self._api.say("", self)
            for disabled, reason in self._plugin_manager.get_disabled().items():
                self._say(
                    "{:<20}: {}".format(
                        disabled,
                        " OR ".join(reason)),
                    self)

    def executor(self, command):
        """
        If command is not empty, we execute it and terminate.
        Else, this method opens a terminal session with the user.
        We can say that it is the core function of this whole class
        and it joins all the function above to work together like a
        clockwork. (Terminates when the user send the "exit", "quit"
        or "goodbye command")
        :return: Nothing to return.
        """
        if command:
            self._jarvis.execute_once(command)
            self.exit()
        else:
            self.cmdloop()


def catch_all_exceptions(do, pass_self=True):
    def try_do(self, s):
        try:
            if pass_self:
                do(self, s)
            else:
                do(s)
        except Exception:
            if self._api.is_spinner_running():
                self.spinner_stop("It seems some error has occured")
            print(
                Fore.RED
                + "Some error occurred, please open an issue on github!")
            print("Here is error:")
            print('')
            traceback.print_exc()
            print(Fore.RESET)
    return try_do
