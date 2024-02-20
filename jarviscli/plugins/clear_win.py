"""
Jarvis plugin for clearing the terminal
"""
from plugin import plugin, require, WINDOWS, UNIX
import os


@require(platform=UNIX)
@plugin("clear")
def clear_unix(jarvis, s):
    # Unix/Linux/MacOS/BSD/etc
    os.system('clear')


@require(platform=WINDOWS)
@plugin("clear")
def clear_windows(jarvis, s):
    # DOS/Windows
    os.system("cls")
