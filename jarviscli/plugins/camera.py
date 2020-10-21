import os

from colorama import Fore

from plugin import Platform, plugin, require


@require(native="cheese", platform=Platform.LINUX)
@plugin('open camera')
def open_camera__LINUX(jarvis, s):
    """Jarvis will open the camera for you."""
    jarvis.say("Opening cheese.......", Fore.RED)
    os.system("cheese")


@require(platform=Platform.MACOS)
@plugin('open camera')
def open_camera__MAC(jarvis, s):
    """Jarvis will open the camera for you."""
    os.system('open /Applications/Photo\\ Booth.app')
