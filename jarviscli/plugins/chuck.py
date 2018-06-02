import requests
from colorama import Fore

from plugin import alias, plugin


@plugin(network=True)
@alias("tell joke")
def chuck(jarvis, s):
    """Tell a joke about Chuck Norris"""
    req = requests.get("https://api.chucknorris.io/jokes/random")
    chuck_json = req.json()

    chuck_fact = chuck_json["value"]
    jarvis.say(chuck_fact, Fore.RED)
