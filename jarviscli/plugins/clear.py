import os
from plugin import plugin


@plugin('clear')
def clear(jarvis, s):
    """Clears terminal"""
    os.system("clear")
