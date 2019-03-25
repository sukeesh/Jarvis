import os
from colorama import Fore
from plugin import plugin, require, LINUX


@require(platform=LINUX, native='ims')
@plugin('movies')
def movies():
    """Jarvis will find a good movie for you"""
    movie_name = input(Fore.RED + "What do you want to watch?\n" + Fore.RESET)
    os.system("ims " + movie_name)
