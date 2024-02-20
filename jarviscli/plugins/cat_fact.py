import requests
from colorama import Fore
from jarviscli import entrypoint


@entrypoint
def cat_fact(jarvis, s):
    """Tells a random cat fact"""

    req = requests.get("https://catfact.ninja/fact")
    data = req.json()

    cat_fact = data["fact"]
    jarvis.say(cat_fact, Fore.BLUE)
