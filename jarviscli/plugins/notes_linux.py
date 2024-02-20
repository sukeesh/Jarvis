import os

from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def open_notes(jarvis, s):
    """Jarvis will open the notes application for you."""
    jarvis.say("Opening notes.......", Fore.GREEN)
    os.system("gedit")
