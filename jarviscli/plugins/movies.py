from plugin import plugin, require, LINUX

from colorama import Fore
import os


@require(platform=LINUX, native='ims')
@plugin('movies')
def movies():
    """Jarvis will find a good movie for you"""
    movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
    os.system("ims " + movie_name)
