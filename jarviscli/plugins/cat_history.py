from colorama import Fore

from Jarvis import HISTORY_FILENAME
from plugin import plugin


@plugin('cat his')
def cat_history(jarvis, s):
    """Prints the history of commands"""
    HISTORY_FILENAME.seek(0)
    history = str(HISTORY_FILENAME.read())
    jarvis.say(history, Fore.BLUE)
