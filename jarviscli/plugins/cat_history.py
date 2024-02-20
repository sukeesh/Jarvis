from colorama import Fore
from core.jarvis import HISTORY_FILENAME
from jarviscli import entrypoint


@entrypoint
def cat_history(jarvis, s):
    """Prints the history of commands"""
    HISTORY_FILENAME.seek(0)
    history = str(HISTORY_FILENAME.read())
    jarvis.say(history, Fore.BLUE)
