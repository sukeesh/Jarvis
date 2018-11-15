from plugin import plugin, require
from six.moves import input
from os import system
from colorama import Fore


@require(native='grep')
@plugin('match')
def match(jarvis, string):
    """
    Matches a string pattern in a file using regex.
    Type "match" and you'll be prompted.
    """
    file_name = input(Fore.RED + "Enter file name?:\n" + Fore.RESET)
    pattern = input(Fore.GREEN + "Enter string:\n" + Fore.RESET)
    file_name = file_name.strip()
    if file_name == "":
        jarvis.say("Invalid Filename")
    else:
        system("grep '" + pattern + "' " + file_name)
