from plugin import plugin

import os


@plugin()
def clear():
    """Clears terminal"""
    os.system("clear")
