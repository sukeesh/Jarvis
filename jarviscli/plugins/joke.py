import requests
from colorama import Fore
from plugin import alias, plugin, require


@alias("tell random joke")
@require(network=True)
@plugin('joke')
def chuck(jarvis, s):
    """Tell a random joke"""
    req = requests.get("https://sv443.net/jokeapi/category/Any")
    res = req.json()

    joke = res["setup"]+"\n"+res["delivery"]
    jarvis.say(joke, Fore.RED)
