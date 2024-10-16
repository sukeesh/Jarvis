import requests
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin("numbersapi")
def numbersapi(jarvis, s):
    """
    numbersapi: Displays API facts
    numbersapi <list of numbers>: Displays facts about each number in list
    numbersapi random trivia: Displays a random trivia fact
    numbersapi random date: Displays a random fact about a date
    numbersapi random year: Displays a random fact about a year
    numbersapi random number: Displays a random number fact
    numbersapi help: Prints this help

    ** Data provided by: http://numbersapi.com/
    """
    parts = s.split(" ")

    if not s or 'help' in parts:
        jarvis.say(numbersapi.__doc__, Fore.GREEN)
        return

    if "random" in parts:
        if "trivia" in parts:
            data = get_data(jarvis, "random/trivia")
        elif "date" in parts:
            data = get_data(jarvis, "random/date")
        elif "year" in parts:
            data = get_data(jarvis, "random/year")
        elif "number" in parts:
            data = get_data(jarvis, "random")
        else:
            jarvis.say("\tInvalid random type. Use 'trivia', 'date', 'year', or 'number'.", Fore.RED)
            return

        if data:
            jarvis.say(f"\t{data}", Fore.CYAN)
        return

    if any((not part.isnumeric() for part in parts)):
        jarvis.say("\tPlease, pass valid integers as arguments.", Fore.RED)
        return

    for number in parts:
        data = get_data(jarvis, number)
        if data:
            jarvis.say(f"\t{data}", Fore.CYAN)


def get_data(jarvis, endpoint):
    base_url = "http://numbersapi.com/"
    try:
        response = requests.get(f"{base_url}{endpoint}")
        return response.text
    except requests.exceptions.RequestException:
        jarvis.say(f"\tCould not get data from {base_url}", Fore.RED)
