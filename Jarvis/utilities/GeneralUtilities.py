# -*- coding: utf-8 -*-
from colorama import Fore


def wordIndex(data, word):
    word_list = data.split()
    return word_list.index(word)


def print_say(text, cmd_interpreter_instance, color=""):
    """
        This method give the jarvis the ability to print a text
        and talk when sound is enable.
        :param color: color of text on CLI
        :param cmd_interpreter_instance: Instance of Command Interpreter
        :param text: the text to print (or talk)
               color: Fore.COLOR (ex Fore.BLUE), color for text
        :return: Nothing to return.
        """

    if cmd_interpreter_instance.enable_voice:
        cmd_interpreter_instance.speech.text_to_speech(text)
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
