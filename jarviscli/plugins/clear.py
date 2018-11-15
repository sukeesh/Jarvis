from plugin import plugin

import os


@plugin('clear')
def clear(jarvis, s):
    """Clears terminal"""
    os.system("clear")
