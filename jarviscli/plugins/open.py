from plugin import plugin, LINUX, MACOS

from colorama import Fore
import os


@plugin(native="cheese", plattform=LINUX)
def open_camera__LINUX(jarvis, s):
    """Jarvis will open the camera for you."""
    jarvis.say("Opening cheese.......", Fore.RED)
    os.system("cheese")


@plugin(plattform=MACOS)
def open_camera__MAC(jarvis, s):
    """Jarvis will open the camera for you."""
    os.system('open /Applications/Photo\ Booth.app')
