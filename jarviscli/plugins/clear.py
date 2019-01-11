from plugin import plugin

import os


@plugin()
def clear(jarvis, s):
    """Clears terminal"""
    os.system("clear")
