import os

from colorama import Fore

from plugin import plugin

FILE_PATH = os.path.abspath(os.path.dirname(__file__))
NUM_NEXT = 100


@plugin("pi")
def next_pi(jarvis, s):
    """
    Give the number of digit for pi
    """
    if s == "":
        s = jarvis.input("Number of digit after dot? ")
    try:
        n = int(s)
    except ValueError:
        jarvis.say("That's not a number")
        return
    else:
        pi_file = open(os.path.join(FILE_PATH, '../data/pi.txt'), 'r')
        pi_number = pi_file.read()
        jarvis.say(pi_number[0:n + 2], Fore.GREEN)
