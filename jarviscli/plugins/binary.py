from plugin import plugin
from colorama import Fore


@plugin("binary")
def binary(jarvis, s):
    """
    Converts an integer into a binary number
    """

    if s == "":
        s = jarvis.input("What's your number? ")

    try:
        n = int(s)
    except ValueError:
        jarvis.say("This is no number, right?", Fore.RED)
        return
    else:
        if n < 0:
            jarvis.say("-" + bin(n)[3:], Fore.YELLOW)
        else:
            jarvis.say(bin(n)[2:], Fore.YELLOW)
