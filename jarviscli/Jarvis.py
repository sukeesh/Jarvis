import os
from colorama import Fore
import nltk
import re
import sys
import tempfile
from utilities.GeneralUtilities import print_say
from CmdInterpreter import CmdInterpreter

HISTORY_FILENAME = tempfile.TemporaryFile('w+t')
PROMPT_CHAR = '~>'

class Jarvis(CmdInterpreter, object):
    first_reaction_text = ""
    first_reaction_text += Fore.CYAN + \
        'Jarvis\' sound is by default disabled.' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.CYAN + 'In order to let Jarvis talk out loud type: '
    first_reaction_text += Fore.RESET + Fore.MAGENTA + 'enable sound' + Fore.RESET
    first_reaction_text += "\n"
    first_reaction_text += Fore.CYAN + \
        "Type 'help' for a list of available actions." + Fore.RESET
    first_reaction_text += "\n"
    prompt = (
        Fore.MAGENTA
        + "{} Hi, what can I do for you?\n".format(PROMPT_CHAR)
        + Fore.RESET)

    def __init__(self, first_reaction_text=first_reaction_text,
                 prompt=prompt, first_reaction=True,
                 directories=["jarviscli/plugins", "custom"]):
        directories = self._rel_path_fix(directories)

        if sys.platform == 'win32':
            self.use_rawinput = False
        self.regex_dot = re.compile('\\.(?!\\w)')
        CmdInterpreter.__init__(self, first_reaction_text, prompt,
                                directories, first_reaction)

    def _rel_path_fix(self, dirs):
        dirs_abs = []
        work_dir = os.path.dirname(__file__)
        work_dir = os.path.dirname(work_dir)

        nltk.data.path.append(os.path.join(work_dir, "jarviscli/data/nltk"))

        for directory in dirs:
            if not directory.startswith(work_dir):
                directory = os.path.join(work_dir, directory)
            dirs_abs.append(directory)
        return dirs_abs

    def default(self, data):
        print_say("I could not identify your command...", self, Fore.MAGENTA)

    def precmd(self, line):
        words = line.split()
        HISTORY_FILENAME.write(line + '\n')

        if words and (words[0].isdigit() or line[0] == "-"):
            line = "calculate " + line
            words = line.split()

        if line.startswith("help") or line.startswith("status"):
            return line

        if not words:
            line = "None"
        else:
            line = self.parse_input(line)
        return line

    def postcmd(self, stop, line):
        if self.first_reaction:
            self.prompt = (
                Fore.MAGENTA
                + "{} What can I do for you?\n".format(PROMPT_CHAR)
                + Fore.RESET)
            self.first_reaction = False
        if self.enable_voice:
            self.speech.text_to_speech("What can I do for you?\n")

    def speak(self, text):
        if self.enable_voice:
            self.speech.text_to_speech(text)

    def parse_input(self, data):
        data = data.lower()
        if "say" not in data:
            data = data.replace("?", "")
            data = data.replace("!", "")
            data = data.replace(",", "")

            data = self.regex_dot.sub("", data)

        if data in self.fixed_responses:
            output = self.fixed_responses[data]
        else:
            output = self.find_action(
                data, self._plugin_manager.get_plugins().keys())
        return output

    def find_action(self, data, actions):
        output = "None"
        if not actions:
            return output

        action_found = False
        words = data.split()
        actions = list(actions)

        actions.sort(key=lambda l: len(l), reverse=True)

        for action in actions:
            words_remaining = data.split()
            for word in words:
                words_remaining.remove(word)
                if word == "near":
                    initial_words = words[:words.index('near')]
                    output = word + " " +\
                        " ".join(initial_words + ["|"] + words_remaining)
                elif word == action:
                    action_found = True
                    output = word + " " + " ".join(words_remaining)
                    break
            if action_found:
                break
        return output

    def executor(self, command):
        if command:
            self.execute_once(command)
        else:
            self.cmdloop()

