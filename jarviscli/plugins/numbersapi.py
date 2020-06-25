import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("numbersapi")
def numbersapi(jarvis, s):
    """
    numbersapi: Displays API
    numbersapi <list of numbers>: Displays facts about each number in list"
    numbersapi help: Prints this help

    ** Data provided by: http://numbersapi.com/
    """
    parts = s.split(" ")

    if not s or 'help' in parts:
        jarvis.say(numbersapi.__doc__, Fore.GREEN)
        return

    if any((not part.isnumeric() for part in parts)):
        jarvis.say("\tPlease, pass valid integers as arguments.", Fore.RED)
        return

    for number in parts:
        data = get_data(jarvis, number)
        if data:
            jarvis.say(f"\t{data}", Fore.CYAN)


def get_data(jarvis, number):
    base_url = "http://numbersapi.com/"
    try:
        response = requests.get(f"{base_url}{number}")
        return response.text
    except requests.exceptions.RequestException:
        jarvis.say(f"\tCould not get data from {base_url}", Fore.RED)
