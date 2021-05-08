"""
Jarvis plugin for clearing the terminal
"""
from plugin import plugin
import os


@plugin("clear")
def clear(jarvis, s):
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system("cls")
