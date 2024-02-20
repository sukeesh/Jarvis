from colorama import Fore
from jarviscli import entrypoint


@entrypoint
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
            jarvis.say("-" + hex(n).upper()[3:], Fore.YELLOW)
        else:
            jarvis.say(hex(n).upper()[2:], Fore.YELLOW)
