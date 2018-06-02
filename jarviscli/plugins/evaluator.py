from math import *  # to give eval access to all of math lib

from colorama import Fore

from plugin import plugin


@plugin()
def calculate(jarvis, s):
    """
    Jarvis will get your calculations done!
    -- Example:
        calculate 3 + 5
    """

    tempt = s.replace(" ", "")
    if len(tempt) > 1:
        calc(jarvis, tempt)
    else:
        jarvis.say("Error: Not in correct format", Fore.RED)


def calc(jarvis, s):
    s = str.lower(s)
    s = s.replace("power", "**")
    s = s.replace("plus", "+")
    s = s.replace("minus", "-")
    s = s.replace("divided by", "/")
    s = s.replace("by", "/")
    s = s.replace("^", "**")
    try:
        x = eval(s)
        jarvis.say(str(x), Fore.BLUE)
    except Exception:
        jarvis.say("Error : Not in correct format")
