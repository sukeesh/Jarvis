# -*- coding: utf-8 -*-
import sys
import os
from six.moves import input
from colorama import Fore
import distutils.spawn


MACOS = 'darwin'
WIN = 'win32'
IS_MACOS = sys.platform == MACOS
IS_WIN = sys.platform == WIN


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
                    print('{}Command is unsupported for platform `{}`{}'.
                          format(Fore.RED, sys.platform, Fore.RESET))
            else:
                func(*args, **kwargs)
        return wrapped
    return noop_wrapper


def executable_exists(name):
    binary_path = distutils.spawn.find_executable(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)
