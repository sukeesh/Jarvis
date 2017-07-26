# -*- coding: utf-8 -*-
from utilities.GeneralUtilities import print_say
from colorama import Fore
from math import *  # to give eval access to all of math lib


def calc(s, self):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("divided by", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")
    try:
        x = eval(s)
        print_say(str(x), self, Fore.BLUE)
    except Exception:
        print_say("Error : Not in correct format", self)
