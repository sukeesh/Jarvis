from plugin import plugin
from colorama import Fore


@plugin("hex")
def binary(jarvis, s):
    """
    Converts an integer into a hexadecimal number
    """

    if s == "":
        s = jarvis.input("What's your number? ")
    try:
        n = int(s)
    except ValueError:
        jarvis.say("That's not a number!", Fore.RED)
        return
    else:
        if n < 0:
            jarvis.say("-" + hex(n)[3:].upper(), Fore.YELLOW)
        else:
            jarvis.say(hex(n)[2:].upper(), Fore.YELLOW)
