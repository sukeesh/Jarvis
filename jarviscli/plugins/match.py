from plugin import plugin, LINUX
from six.moves import input
from os import system
from colorama import Fore


@plugin(native='grep')
def match(jarvis, string):
    """
    Matches a string pattern in a file using regex.
    Type "match" and you'll be prompted.
    """
    file_name = jarvis.input("Enter file name?:\n", Fore.RED)
    pattern = jarvis.input("Enter string:\n", Fore.GREEN)
    file_name = file_name.strip()
    if file_name == "":
        jarvis.say("Invalid Filename")
    else:
        system("grep '" + pattern + "' " + file_name)
