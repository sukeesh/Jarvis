import signal
import sys
import traceback
from cmd import Cmd

import colorama
from colorama import Fore

from utilities.animations import SpinnerThread

PROMPT_CHAR = '~>'


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

        # enable color on windows
        colorama.init()
        # change raw input based on os
        if sys.platform == 'win32':
            self.use_rawinput = False

        self.first_reaction = True

        # Register do_quit() function to SIGINT signal (Ctrl-C)
        signal.signal(signal.SIGINT, self.interrupt_handler)
        self.first_reaction_text += self._jarvis.plugin_info()

        for plugin in self._jarvis.get_plugins().values():
            self._add_plugin(plugin)

        self.say(self.first_reaction_text)

    def say(self, text, color=''):
        print(color + text + Fore.RESET, flush=True)

    def start(self):
        self.cmdloop()

    def stop(self):
        # to be implemented
        pass

    def input(self, prompt="", color=""):
        # we can't use input because for some reason input() and color codes do not work on
        # windows cmd
        sys.stdout.write(color + prompt + Fore.RESET)
        sys.stdout.flush()
        text = sys.stdin.readline()
        # return without newline
        return text.rstrip()

    def spinner_start(self, message="Starting "):
        self.spinner = SpinnerThread(message, 0.15)
        self.spinner.start()

    def spinner_stop(self, message="Task executed successfully! ", color=Fore.GREEN):
        self.spinner.stop()
        self.say(message, color)

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
        self.say(self.prompt)

    def error(self):
        """Jarvis let you know if an error has occurred."""
        self.say("I could not identify your command...", Fore.RED)

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        self._jarvis.exit()

    def do_status(self, s):
        """Prints plugin status status"""


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
