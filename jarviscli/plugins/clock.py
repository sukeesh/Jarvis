from time import ctime

from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def clock(jarvis, s):
    """Gives information about time"""
    jarvis.say(ctime(), Fore.BLUE)
