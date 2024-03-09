"""
Jarvis plugin for clearing the terminal
"""
import os

from jarviscli import entrypoint


@entrypoint
def clear_windows(jarvis, s):
    # DOS/Windows
    os.system("cls")
