# -*- coding: utf-8 -*-
import re
from colorama import Fore
from plugin import plugin


@plugin('tempconv')
class Tempconv():
    """
    Convert temperature from Fahrenheit to Celsius and vice versa
    Examples: 32f, 18C, -20F, -8c, 105.4F, -10.21C
    """

    def __call__(self, jarvis, s):
        # Pass the input string to the regex validation function.
        if self.temp_valid_regex(s):
            self.temp_convert(jarvis, s)

        # Print an error if the input string fails the regex test.
        else:
            jarvis.say(
                "I'm sorry, invalid input. Please see \"help tempconv\" for syntax.",
                Fore.RED)

    def temp_valid_regex(self, s):
        """Validate the input string using regex and return a boolean for validity"""
        if re.search("^-?\\d+(\\.\\d+)?[FfCc]$", s):
            return True
        else:
            return False

    def temp_convert(self, jarvis, s):
        """Assuming valid regex, handle the actual temperature conversion and output"""

        # convert the string into a float
        starting_temp = float(s[:-1])

        # run conversions and create output string.
        if s[-1].lower() == 'f':
            new_temp = self.convert_f_to_c(starting_temp)
            output = "{}° F is {}° C".format(starting_temp, new_temp)
        else:
            new_temp = self.convert_c_to_f(starting_temp)
            output = "{}° C is {}° F".format(starting_temp, new_temp)

        # use print_say to display the output string
        jarvis.say(output, Fore.BLUE)

    def convert_f_to_c(self, starting_temp):
        """Convert from Fahrenheit to Celsius"""
        return round(((starting_temp - 32) * 5 / 9), 2)

    def convert_c_to_f(self, starting_temp):
        """Convert from Celsius to Fahrenheit"""
        return round((starting_temp * 9 / 5 + 32), 2)
