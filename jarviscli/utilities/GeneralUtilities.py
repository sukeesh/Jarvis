# -*- coding: utf-8 -*-
import distutils.spawn
import os
from platform import win32_ver
import json
import sys
import warnings

from colorama import Fore

USER_THEME_FILEPATH = "jarviscli/data/user_theme.json"
MACOS = 'darwin'
WIN = 'win32'
IS_MACOS = sys.platform == MACOS
IS_WIN = sys.platform == WIN
WIN_VER = None
if IS_WIN:
    WIN_VER = win32_ver()[0]

def get_user_theme(filepath=USER_THEME_FILEPATH):
    """
        Returns a dictionary corresponding to the current user theme.
        :param filepath: the filepath to the JSON theme file
    """
    # Load user-theme from JSON
    f = open(filepath)
    data = json.load(f)
    return data['current']

def theme_option(option):
    """
        Returns a color corresponding to specified theme option.
        :param option: a string specifying the theme option 
        (greeting, default_text, info, negative_text, positive_text)
    """
    theme = get_user_theme()
    return theme[option]

def print_say(text, self, color=""):
    """
        Gives Jarvis the ability to print text
        and talk when sound is enabled.
        :param text: the text to print (or talk)
               color: Fore.COLOR (ex Fore.BLUE), color for text
        :return: Nothing to return.

        .. deprecated::
            Use ``JarvisAPI.say(text, color="", speak=True))`` instead.
    """
    warnings.warn(
        "GeneralUtilities.print_say is deprecated now and will be \
        removed in the future. Please use \
        ``JarvisAPI.say(text, color=\"\", speak=True))`` instead.",
        DeprecationWarning)
    print(color + text + theme_option('reset_text'))
    if self.enable_voice:
        self.speech.text_to_speech(text)


# Functions for printing user output
# TODO decide which ones use print_say instead of print
def critical(string):
    print(theme_option('negative_text') + string + theme_option('reset_text'))


def error(string):
    critical(string)


def important(string):
    print(theme_option('greeting') + string + theme_option('reset_text'))


def warning(string):
    important(string)


def info(string):
    print(theme_option('info') + string + theme_option('reset_text'))


def unsupported(platform, silent=False):
    def noop_wrapper(func):
        def wrapped(*args, **kwargs):
            if sys.platform == platform:
                if not silent:
                    print(
                        '{}Command is unsupported for platform `{}`{}'.format(
                            theme_option('negative_text'), sys.platform, theme_option('reset_text')))
            else:
                func(*args, **kwargs)

        return wrapped

    return noop_wrapper


def executable_exists(name):
    binary_path = distutils.spawn.find_executable(name)
    return binary_path is not None and os.access(binary_path, os.X_OK)


def get_parent_directory(path):
    """
    Removes the file name from the folder and returns
    the remaining path
    """
    path = path.split('/')
    path.pop()
    destination = '/'.join(path)
    return destination
