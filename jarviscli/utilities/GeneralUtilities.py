# -*- coding: utf-8 -*-
import sys
from functools import wraps

from colorama import Fore

MACOS = 'darwin'
IS_MACOS = sys.platform == MACOS


def wordIndex(data, word):
    wordList = data.split()
    return wordList.index(word)


def print_say(text, self, color=""):
    """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param text: the text to print (or talk)
               color: Fore.COLOR (ex Fore.BLUE), color for text
        :return: Nothing to return.
        """
    if self.enable_voice:
        self.speech.text_to_speech(text)
    print(color + text + Fore.RESET)


# Functions for printing user output
# TODO decide which ones use print_say instead of print
def critical(string):
    print(Fore.RED + string + Fore.RESET)


def error(string):
    critical(string)


def important(string):
    print(Fore.YELLOW + string + Fore.RESET)


def warning(string):
    important(string)


def info(string):
    print(Fore.BLUE + string + Fore.RESET)


def unsupported(platform, silent=False):
    def noop_wrapper(func):
        def wrapped(*args, **kwargs):
            if sys.platform == platform:
                if not silent:
                    print(
                        Fore.RED +
                        'Command is unsupported for platform `{}`'.format(
                            sys.platform
                        ) + Fore.RESET)
            else:
                func(*args, **kwargs)
        return wrapped
    return noop_wrapper
