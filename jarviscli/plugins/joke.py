import requests
from colorama import Fore
from plugin import alias, plugin, require


@alias("tell me random any joke")
@require(network=True)
@plugin('joke')
def chuck(jarvis, s):
    """Tell a joke random"""
    req = requests.get("https://sv443.net/jokeapi/category/Any")
    joke = req.json()

    jokeSetup = joke["setup"]
    jokeDelivery = joke["delivery"]


    joke = jokeSetup+jokeDelivery
    jarvis.say(joke, Fore.RED)
