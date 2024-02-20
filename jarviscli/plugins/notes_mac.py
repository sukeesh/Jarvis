import os

from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def open_notes__MAC(jarvis, s):
    """Jarvis will open the Notes app for you."""
    jarvis.say("Opening Notes.......", Fore.GREEN)
    os.system('open /Applications/Notes.app')
