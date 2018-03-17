# -*- coding: utf-8 -*-

from utilities.GeneralUtilities import print_say
from colorama import Fore
import re


def temp_main(self, s):
    """Handles the initial call from Jarvis CLI"""

    # Pass the input string to the regex validation function.
    if temp_valid_regex(s):
        temp_convert(self, s)

    # Print an error if the input string fails the regex test.
    else:
        print_say("I'm sorry, invalid input. Please see \"help tempconv\" for syntax.", self, Fore.RED)


def temp_valid_regex(s):
    """Validate the input string using regex and return a boolean for validity"""
    if re.search("^-?\d+(\.\d+)?[FfCc]$", s):
        return True
    else:
        return False


def temp_convert(self, s):
    """Assuming valid regex, handle the actual temperature conversion and output"""

    # convert the string into a float
    starting_temp = float(s[:-1])

    # run conversions and create output string.
    if s[-1].lower() == 'f':
        new_temp = convert_f_to_c(starting_temp)
        output = "{}° F is {}° C".format(starting_temp, new_temp)
    else:
        new_temp = convert_c_to_f(starting_temp)
        output = "{}° C is {}° F".format(starting_temp, new_temp)

    # use print_say to display the output string
    print_say(output, self, Fore.BLUE)


def convert_f_to_c(starting_temp):
    """Convert from Fahrenheit to Celsius"""
    return round(((starting_temp - 32) * 5 / 9), 2)


def convert_c_to_f(starting_temp):
    """Convert from Celsius to Fahrenheit"""
    return round((starting_temp * 9 / 5 + 32), 2)
