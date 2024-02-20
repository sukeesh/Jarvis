import os

from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def open_camera__LINUX(jarvis, s):
    """Jarvis will open the camera for you."""
    jarvis.say("Opening cheese.......", Fore.RED)
    os.system("cheese")
