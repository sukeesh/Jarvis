import pyjokes
from colorama import Fore
from plugin import plugin, require


@require(network=True)
@plugin('joke')
def joke(jarvis, s):
    """Tells a random joke"""
    joke = pyjokes.get_joke()

    jarvis.say(joke, Fore.BLUE)
