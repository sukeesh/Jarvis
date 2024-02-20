"""
Jarvis plugin for clearing the terminal
"""
import os

from jarviscli import entrypoint


@entrypoint
def clear_unix(jarvis, s):
    # Unix/Linux/MacOS/BSD/etc
    os.system('clear')
