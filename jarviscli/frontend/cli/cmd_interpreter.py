import signal
import sys
import traceback
from cmd import Cmd
from getpass import getpass

import colorama
from colorama import Fore

import inquirer
from frontend.cli.spinner import SpinnerThread
from utilities.cli import cancel, input

PROMPT_CHAR = '~>'


class CmdInterpreter(Cmd):
    """
    Cmd source code:
    https://github.com/python/cpython/blob/master/Lib/cmd.py
    """

    first_reaction_text = """\
{BLUE}Jarvis' sound is by default disabled.{RESET}
{BLUE}In order to let Jarvis talk out load type:{RESET}{RED}enable sound{RESET}
Type 'help' for a list of available actions.
""".format(BLUE=Fore.BLUE, RESET=Fore.RESET, RED=Fore.RED)

    prompt_msg = (
        Fore.RED
        + "{} Hi, what can I do for you?\n".format(PROMPT_CHAR)
        + Fore.RESET)
    prompt = ''

    def __init__(self, jarvis):
        """
        This constructor contains a dictionary with Jarvis Actions (what Jarvis can do).
        In alphabetically order.
        """
        super().__init__()

        self._jarvis = jarvis

        # enable color on windows
        colorama.init()
        self.first_reaction = True

        # Register do_quit() function to SIGINT signal (Ctrl-C)
        signal.signal(signal.SIGINT, self.interrupt_handler)
        self.first_reaction_text += self._jarvis.dependency_status.print_count()
        self.first_reaction_text += '  More information: {red}status{reset}\n'.format(
            red=Fore.RED, reset=Fore.RESET)

        for plugin in self._jarvis.get_plugins().values():
            self._add_plugin(plugin)

        self.say(self.first_reaction_text)

        self._do_stop = False
        self._cancel_input = False

    def say(self, text, color=''):
        print(color + text + Fore.RESET, flush=True)

    def show_prompt(self):
        """Hook that executes after every command."""
        if self.first_reaction:
            self.prompt_msg = (
                Fore.RED
                + "{} What can I do for you?\n".format(PROMPT_CHAR)
                + Fore.RESET)
            self.first_reaction = False
        self.say(self.prompt_msg)

    def start(self):
        try:
            import readline
            self.old_completer = readline.get_completer()
            readline.set_completer(self.complete)
            readline.parse_and_bind(self.completekey + ": complete")
        except ImportError:
            pass

        while not self._do_stop:
            line = input(self.prompt)
            if not len(line):
                line = 'EOF'
            line = self.precmd(line)
            stop = self.onecmd(line)
            stop = self.postcmd(stop, line)
        self.postloop()

    def stop(self):
        self._do_stop = True
        # cancel input
        cancel()

    def postcmd(self, *args):
        super().postcmd(*args)
        return self._do_stop

    def input(self, _prompt="", color="", password=False):
        # color even for windows cmd
        sys.stdout.write(color + _prompt + Fore.RESET)
        sys.stdout.flush()

        if password:
            return getpass()
        return input()

    def choose(self, options_dict):
        def build_question(key, text, params):
            if isinstance(params, list):
                return inquirer.Checkbox(key, message=text, choices=params)
            if isinstance(params, set):
                return inquirer.List(key, message=text, choices=params)
            elif isinstance(params, str):
                return inquirer.Text(key, message=text, default=value)
            elif params is None:
                return inquirer.confirm(message=text)
            assert False, 'unknown parameter for choose'

        questions = [build_question(key, text, params) for key, (text, params) in options_dict.items()]
        return inquirer.prompt(questions)

    def choose_path(self, message):
        return inquirer.prompt(inquirer.Path('file', message=message))['file']

    def spinner_start(self, message="Starting "):
        self.spinner = SpinnerThread(message, 0.15)
        self.spinner.start()

    def spinner_stop(self, message="Task executed successfully! ", color=Fore.GREEN):
        self.spinner.stop()
        self.say(message, color)

    def _add_plugin(self, plugin):

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
        self._jarvis.execute_once(s)

    def interrupt_handler(self, signal, frame):
        """Closes Jarvis on SIGINT signal. (Ctrl-C)"""
        try:
            self._jarvis.exit()
        except SystemExit:
            pass

    def do_status(self, s):
        """Prints plugin status status"""
