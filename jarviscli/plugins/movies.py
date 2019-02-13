from plugin import plugin, LINUX

from colorama import Fore
import os


@plugin(plattform=LINUX, native='ims')
def movies():
    """Jarvis will find a good movie for you"""
    movie_name = jarvis.input("What do you want to watch?\n", Fore.RED)
    os.system("ims " + movie_name)
