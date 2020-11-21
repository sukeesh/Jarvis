from colorama import Fore
# All plugins should inherite from this library
from plugin import plugin


@plugin("workspace")
def generate_workspace(jarvis, s):
