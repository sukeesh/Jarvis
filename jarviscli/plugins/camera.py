from plugin import plugin, require, LINUX, MACOS

from colorama import Fore
import os


@require(native="cheese", platform=LINUX)
@plugin
def open_camera__LINUX(jarvis, s):
    """Jarvis will open the camera for you."""
    jarvis.say("Opening cheese.......", Fore.RED)
    os.system("cheese")


@require(platform=MACOS)
@plugin
def open_camera__MAC(jarvis, s):
    """Jarvis will open the camera for you."""
    os.system('open /Applications/Photo\\ Booth.app')
