from utilities.GeneralUtilities import IS_WIN

# handle readline import based on os
if IS_WIN:
    from pyreadline import Readline
    readline = Readline()
else:
    import readline

from colorama import Fore
from plugin import plugin


@plugin('cat his')
def cat_history(jarvis, s):
    """Prints the history of commands"""

    cat_history = get_history_items()
    history = '\n'.join(cat_history)
    jarvis.say(history, Fore.BLUE)

# collect the commands typed
def get_history_items():
    return [ readline.get_history_item(i)
             for i in range(1, readline.get_current_history_length() + 1)
            ]